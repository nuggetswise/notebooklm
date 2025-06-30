import time
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pytz
import os
import sys
from pathlib import Path
import json
import psutil

from .models import (
    EmailProcessingResponse, EmailStatusResponse, EmailContent,
    QueryRequest, QueryResponse, RefreshResponse, EmailMetadata, PersonaInfo
)
from .parser import parser
from .database import db
from .config import config

# Initialize FastAPI app
app = FastAPI(
    title="Email Processing & RAG API",
    description="API for processing auto-forwarded emails and running RAG-based Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance (initialized lazily)
_rag_pipeline = None

def get_rag_pipeline():
    """Get or create RAG pipeline instance - LAZY LOADING for Cloud Run."""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            sys.path.append(str(Path(__file__).parent.parent))
            from rag.email_pipeline import pipeline
            _rag_pipeline = pipeline
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize RAG pipeline: {e}")
            return None
    return _rag_pipeline

@app.on_event("startup")
async def startup_event():
    """Lightweight startup for Cloud Run - no heavy initialization."""
    print("🚀 Email Processing & RAG API starting up (Cloud Run optimized)...")
    print(f"📁 Data directory: {config.DATA_DIR}")
    print(f"📧 Parsed emails directory: {config.PARSED_EMAILS_DIR}")
    print(f"📂 Maildir directory: {config.MAILDIR_DIR}")
    
    # Don't initialize RAG pipeline on startup - do it lazily on first use
    print("🔄 RAG pipeline will be initialized on first use (lazy loading)")
    
    # Just ensure directories exist
    try:
        config.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        config.PARSED_EMAILS_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ Directories created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not create directories: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Email Processing & RAG API (Cloud Run)",
        "version": "1.0.0",
        "endpoints": {
            "POST /inbound-email": "Process incoming MIME email",
            "GET /status": "Get email status and metadata",
            "GET /email/{id}/content": "Get parsed email content",
            "POST /refresh": "Reprocess emails from maildir",
            "POST /query": "Query emails using RAG",
            "GET /rag/stats": "Get RAG pipeline statistics"
        }
    }

@app.post("/inbound-email", response_model=EmailProcessingResponse)
async def process_inbound_email(request: Request):
    """Process incoming MIME email from smtp2http or direct forward."""
    start_time = time.time()
    try:
        # Read raw email from body
        raw_email = await request.body()
        if not raw_email:
            raise HTTPException(status_code=400, detail="Empty email content")
        
        # Parse email
        email_data = parser.parse_email(raw_email)
        
        # Check if email is within age limit
        email_date = email_data['date']
        if email_date.tzinfo is None:
            email_date = email_date.replace(tzinfo=pytz.UTC)
        now_utc = datetime.utcnow().replace(tzinfo=email_date.tzinfo)
        if email_date < now_utc - timedelta(days=config.MAX_AGE_DAYS):
            return EmailProcessingResponse(
                success=False,
                email_id="",
                message=f"Email too old (received {email_date.date()}, max age: {config.MAX_AGE_DAYS} days)",
                processing_time=time.time() - start_time
            )
        
        # Generate email ID
        email_id = str(uuid.uuid4())
        
        # Save parsed email to file (use /tmp for Cloud Run)
        parsed_path = parser.save_parsed_email(email_data, email_id)
        if not parsed_path:
            raise HTTPException(status_code=500, detail="Failed to save parsed email")
        
        # Create email metadata
        email_metadata = EmailMetadata(
            id=email_id,
            subject=email_data['subject'],
            sender=email_data['sender'],
            date=email_data['date'],
            label=email_data['label'],
            parsed_path=parsed_path,
            has_attachments=email_data['has_attachments'],
            attachment_count=email_data['attachment_count'],
            has_media=email_data.get('has_media', False),
            media_urls=email_data.get('media_urls', {'images': [], 'videos': [], 'iframes': []}),
            persona=PersonaInfo(**email_data['persona']) if email_data.get('persona') else None
        )
        
        # Save to database
        if not db.insert_email(email_metadata):
            raise HTTPException(status_code=500, detail="Failed to save email metadata")
        
        processing_time = time.time() - start_time
        return EmailProcessingResponse(
            success=True,
            email_id=email_id,
            message=f"Email processed successfully. Subject: {email_data['subject']}",
            metadata=email_metadata,
            processing_time=processing_time
        )
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Error processing email: {e}")
        return EmailProcessingResponse(
            success=False,
            email_id="",
            message=f"Error processing email: {str(e)}",
            processing_time=processing_time
        )

@app.get("/status", response_model=EmailStatusResponse)
async def get_email_status(
    label: Optional[str] = Query(None, description="Filter by label"),
    max_age_days: Optional[int] = Query(config.MAX_AGE_DAYS, description="Maximum age in days")
):
    """Get email status and metadata - filtered to substack.com only."""
    try:
        # Always filter to substack.com unless explicitly overridden
        if not label:
            label = "substack.com"
        
        if label:
            emails = db.get_emails_by_label(label, max_age_days)
        else:
            emails = db.get_all_emails(max_age_days)
        
        # Get all labels for frontend (but only substack.com)
        all_labels = ["substack.com"]
        
        # Get total email count (only substack.com)
        total_emails = len(db.get_emails_by_label("substack.com", max_age_days))
        
        return EmailStatusResponse(
            emails=emails,
            total_count=len(emails),
            total_emails=total_emails,
            labels=all_labels,
            label_filter=label,
            max_age_days=max_age_days
        )
        
    except Exception as e:
        print(f"Error getting email status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving email status: {str(e)}")

@app.get("/email/{email_id}/content", response_model=EmailContent)
async def get_email_content(email_id: str):
    """Get parsed email content by ID."""
    try:
        # Get email metadata
        email_metadata = db.get_email_by_id(email_id)
        if not email_metadata:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Read parsed content from file
        try:
            with open(email_metadata.parsed_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Email content file not found")
        
        # Extract body content (everything after the metadata header)
        lines = content.split('\n')
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('-' * 80):
                body_start = i + 2
                break
        
        body = '\n'.join(lines[body_start:])
        
        return EmailContent(
            id=email_metadata.id,
            subject=email_metadata.subject,
            sender=email_metadata.sender,
            date=email_metadata.date,
            body=body,
            label=email_metadata.label,
            attachments=[]  # TODO: Add attachment info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting email content: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving email content: {str(e)}")

@app.get("/labels")
async def get_available_labels():
    """Get available email labels - filtered to substack.com only."""
    try:
        labels = db.get_labels()
        # Filter to only show substack.com
        filtered_labels = [label for label in labels if label == "substack.com"]
        return {
            "labels": filtered_labels,
            "count": len(filtered_labels)
        }
    except Exception as e:
        print(f"Error getting labels: {e}")
        return {"labels": ["substack.com"], "count": 1}

@app.get("/emails")
async def get_emails(
    label: Optional[str] = Query(None, description="Filter by label"),
    since: Optional[str] = Query(None, description="Filter emails since this date (ISO format)"),
    max_age_days: Optional[int] = Query(30, description="Maximum age in days")
):
    """Get emails with optional filtering."""
    try:
        if label:
            emails = db.get_emails_by_label(label, max_age_days)
        else:
            emails = db.get_all_emails(max_age_days)
        
        # Filter by date if specified
        if since:
            try:
                since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
                filtered_emails = []
                for email in emails:
                    email_date = email.date
                    if isinstance(email_date, str):
                        email_date = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
                    if email_date >= since_date:
                        filtered_emails.append(email)
                emails = filtered_emails
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        return {
            "emails": emails,
            "count": len(emails),
            "label": label,
            "since": since,
            "max_age_days": max_age_days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting emails: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving emails: {str(e)}")

@app.post("/refresh", response_model=RefreshResponse)
async def refresh_emails():
    """Reprocess emails from maildir - simplified for Cloud Run."""
    try:
        # For Cloud Run, we'll just return a message since we can't access maildir
        return RefreshResponse(
            success=True,
            message="Email refresh not available in Cloud Run (no persistent maildir access)",
            processed_count=0,
            processing_time=0.0
        )
    except Exception as e:
        print(f"Error refreshing emails: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing emails: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query emails using RAG - with lazy initialization for Cloud Run."""
    start_time = time.time()
    try:
        # Get RAG pipeline (lazy initialization)
        pipeline = get_rag_pipeline()
        if pipeline is None:
            raise HTTPException(status_code=500, detail="RAG pipeline not available")
        
        # Perform query
        result = pipeline.query(
            question=request.query,
            label=request.label,
            max_age_days=request.max_age_days,
            use_cache=True
        )
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            answer=result.get('answer', 'No answer generated'),
            context=result.get('context', []),
            metadata=result.get('metadata', {}),
            processing_time=processing_time,
            provider=result.get('provider', 'unknown'),
            model=result.get('model', 'unknown')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/rag/stats")
async def get_rag_stats():
    """Get RAG pipeline statistics."""
    try:
        pipeline = get_rag_pipeline()
        if pipeline is None:
            return {"error": "RAG pipeline not available"}
        
        stats = pipeline.get_stats()
        return {
            "pipeline_stats": stats,
            "memory_usage_mb": stats.get('memory_usage_mb', 0),
            "documents_loaded": stats.get('documents_loaded', 0),
            "queries_processed": stats.get('queries_processed', 0)
        }
    except Exception as e:
        print(f"Error getting RAG stats: {e}")
        return {"error": f"Error retrieving RAG stats: {str(e)}"}

@app.get("/health")
async def health_check():
    """Lightweight health check for Cloud Run."""
    try:
        # Don't check RAG pipeline on health check - keep it simple
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "cloud-run",
            "database": "connected" if db else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/personas", response_model=List[Dict[str, Any]])
async def get_all_personas():
    """Get all personas."""
    try:
        from .persona_extractor import persona_extractor
        return persona_extractor.get_all_personas()
    except Exception as e:
        print(f"Error getting personas: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving personas: {str(e)}")

@app.get("/personas/{persona_id}", response_model=Dict[str, Any])
async def get_persona_by_id(persona_id: str):
    """Get persona by ID."""
    try:
        from .persona_extractor import persona_extractor
        persona = persona_extractor.get_persona_by_id(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        return persona
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting persona: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving persona: {str(e)}")

@app.get("/personas/sender/{sender:path}", response_model=Dict[str, Any])
async def get_persona_by_sender(sender: str):
    """Get persona by sender email."""
    try:
        from .persona_extractor import persona_extractor
        persona = persona_extractor.get_persona(sender)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        return persona
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting persona: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving persona: {str(e)}")

@app.get("/personas/context/{sender:path}")
async def get_persona_context(sender: str):
    """Get contextual information about a sender for RAG queries."""
    try:
        from .persona_extractor import persona_extractor
        context = persona_extractor.get_persona_context(sender)
        return {"context": context}
    except Exception as e:
        print(f"Error getting persona context: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving persona context: {str(e)}")

@app.get("/prompts", response_model=Dict[str, Dict])
async def get_all_prompts():
    """Get all available prompts with their metadata."""
    try:
        from rag.prompts import prompt_manager
        
        # Get all prompts with full metadata
        prompts = {}
        for prompt_id in ["retrieval", "generation"]:
            prompt_info = prompt_manager.get_prompt_info(prompt_id)
            if prompt_info:
                prompts[prompt_id] = {
                    'name': prompt_info.get('name', ''),
                    'description': prompt_info.get('description', ''),
                    'parameters': prompt_info.get('parameters', []),
                    'category': prompt_info.get('category', ''),
                    'created': prompt_info.get('created', ''),
                    'updated': prompt_info.get('updated', '')
                }
        
        return prompts
    except Exception as e:
        print(f"Error getting prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompts: {str(e)}")

@app.get("/prompts/{prompt_id}")
async def get_prompt_template(prompt_id: str):
    """Get a specific prompt template."""
    try:
        from rag.prompts import prompt_manager
        
        # Get prompt info
        prompt_info = prompt_manager.get_prompt_info(prompt_id)
        if not prompt_info:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")
        
        return {
            'id': prompt_id,
            'name': prompt_info.get('name', ''),
            'template': prompt_info.get('template', ''),
            'description': prompt_info.get('description', ''),
            'parameters': prompt_info.get('parameters', []),
            'category': prompt_info.get('category', ''),
            'created': prompt_info.get('created', ''),
            'updated': prompt_info.get('updated', '')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompt template: {str(e)}")

@app.post("/prompts/{prompt_id}")
async def update_prompt_template(prompt_id: str, request: Dict[str, str]):
    """Update a prompt template."""
    try:
        from rag.prompts import prompt_manager
        
        # Check if prompt exists
        if not prompt_manager.get_prompt_info(prompt_id):
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")
        
        # Validate request
        if 'template' not in request:
            raise HTTPException(status_code=400, detail="Template is required")
        
        # For now, we'll return a message that manual JSON editing is required
        return {
            "message": f"Prompt '{prompt_id}' update requested. Please edit rag/prompts.json manually to update the template.",
            "note": "Automatic updates not yet implemented. Edit the JSON file directly."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating prompt template: {str(e)}")

@app.get("/prompts/test/{prompt_id}")
async def test_prompt_template(prompt_id: str, request: Request):
    """Test a prompt template with provided variables."""
    try:
        from rag.prompts import prompt_manager
        
        # Check if prompt exists
        if not prompt_manager.get_prompt_info(prompt_id):
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        # Get formatted prompt
        formatted_prompt = prompt_manager.format_prompt(prompt_id, **query_params)
        if formatted_prompt is None:
            raise HTTPException(status_code=400, detail="Failed to format prompt - check required parameters")
        
        return {
            'prompt_id': prompt_id,
            'formatted_prompt': formatted_prompt,
            'variables_used': query_params
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error testing prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing prompt template: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics and performance metrics."""
    try:
        # Get RAG pipeline stats
        pipeline = get_rag_pipeline()
        rag_stats = pipeline.get_stats() if pipeline else {}
        
        # Get document counts
        email_files = list(Path(config.PARSED_EMAILS_DIR).glob("*.txt"))
        total_emails = len(email_files)
        
        # Get database stats
        db_stats = {}
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            
            # Email stats
            cursor.execute("SELECT COUNT(*) FROM emails")
            db_emails = cursor.fetchone()[0]
            
            # Label stats
            cursor.execute("SELECT label, COUNT(*) FROM emails GROUP BY label")
            label_counts = dict(cursor.fetchall())
            
            # Date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM emails")
            date_range = cursor.fetchone()
            
            db_stats = {
                'total_emails': db_emails,
                'label_distribution': label_counts,
                'date_range': {
                    'earliest': date_range[0] if date_range[0] else None,
                    'latest': date_range[1] if date_range[1] else None
                }
            }
            
            conn.close()
        except Exception as e:
            db_stats = {'error': str(e)}
        
        # Get file system stats
        vector_store_size = 0
        if Path(config.VECTOR_STORE_DIR / "faiss_index.bin").exists():
            vector_store_size = Path(config.VECTOR_STORE_DIR / "faiss_index.bin").stat().st_size
        
        parsed_emails_size = sum(f.stat().st_size for f in email_files)
        
        # Get memory usage
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        
        return {
            "system": {
                "memory_usage_mb": round(memory_usage, 2),
                "cpu_percent": process.cpu_percent(),
                "uptime_seconds": time.time() - process.create_time()
            },
            "rag_pipeline": rag_stats,
            "database": db_stats,
            "files": {
                "total_emails": total_emails,
                "vector_store_size_bytes": vector_store_size,
                "parsed_emails_size_bytes": parsed_emails_size
            },
            "environment": "cloud-run"
        }
        
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {"error": f"Error retrieving system stats: {str(e)}"}

@app.get("/performance")
async def get_performance_metrics():
    """Get performance metrics and recommendations."""
    try:
        # Get basic system metrics
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Get RAG pipeline stats
        pipeline = get_rag_pipeline()
        rag_stats = pipeline.get_stats() if pipeline else {}
        
        # Calculate efficiency metrics
        efficiency_metrics = {
            "memory_efficiency": "good" if memory_usage < 512 else "high",
            "cpu_usage": "low" if cpu_percent < 10 else "moderate",
            "cache_hit_rate": rag_stats.get('cache_hits', 0) / max(rag_stats.get('queries_processed', 1), 1) * 100
        }
        
        # Get embedder stats
        embedder_stats = {}
        if pipeline and hasattr(pipeline, 'embedder'):
            embedder_stats = {
                "embeddings_generated": rag_stats.get('embeddings_generated', 0),
                "provider": getattr(pipeline.embedder, 'current_provider', 'unknown')
            }
        
        # Generate recommendations
        recommendations = _get_performance_recommendations(efficiency_metrics, embedder_stats)
        
        return {
            "metrics": {
                "memory_usage_mb": round(memory_usage, 2),
                "cpu_percent": round(cpu_percent, 2),
                "efficiency": efficiency_metrics
            },
            "rag_performance": rag_stats,
            "embedder_stats": embedder_stats,
            "recommendations": recommendations,
            "environment": "cloud-run"
        }
        
    except Exception as e:
        print(f"Error getting performance metrics: {e}")
        return {"error": f"Error retrieving performance metrics: {str(e)}"}

def _get_performance_recommendations(efficiency_metrics: dict, embedder_stats: dict) -> List[str]:
    """Generate performance recommendations."""
    recommendations = []
    
    if efficiency_metrics["memory_efficiency"] == "high":
        recommendations.append("Consider reducing memory usage by optimizing document loading")
    
    if efficiency_metrics["cpu_usage"] == "moderate":
        recommendations.append("CPU usage is moderate - consider optimizing heavy operations")
    
    if efficiency_metrics["cache_hit_rate"] < 50:
        recommendations.append("Low cache hit rate - consider increasing cache size or optimizing queries")
    
    if embedder_stats.get("embeddings_generated", 0) > 1000:
        recommendations.append("High number of embeddings generated - consider caching more aggressively")
    
    if not recommendations:
        recommendations.append("Performance looks good! No immediate optimizations needed.")
    
    return recommendations

@app.post("/optimize")
async def optimize_system():
    """Optimize system performance."""
    try:
        # Clear caches
        pipeline = get_rag_pipeline()
        if pipeline:
            pipeline.clear_cache()
        
        return {
            "message": "System optimization completed",
            "actions_taken": ["Cleared RAG pipeline cache"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error optimizing system: {e}")
        raise HTTPException(status_code=500, detail=f"Error optimizing system: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080"))) 