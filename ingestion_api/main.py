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
from .config import settings

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
    """Get or create RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        sys.path.append(str(Path(__file__).parent.parent))
        from rag.email_pipeline import pipeline
        _rag_pipeline = pipeline
    return _rag_pipeline

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Email Processing & RAG API starting up...")
    print(f"📁 Data directory: {settings.DATA_DIR}")
    print(f"📧 Parsed emails directory: {settings.PARSED_EMAILS_DIR}")
    print(f"📂 Maildir directory: {settings.MAILDIR_DIR}")
    
    # Initialize RAG pipeline
    print("🧠 Initializing RAG pipeline...")
    pipeline = get_rag_pipeline()
    pipeline.initialize()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Email Processing & RAG API",
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
        # Ensure both datetimes are timezone-aware (UTC)
        if email_date.tzinfo is None:
            email_date = email_date.replace(tzinfo=pytz.UTC)
        now_utc = datetime.utcnow().replace(tzinfo=email_date.tzinfo)
        if email_date < now_utc - timedelta(days=settings.MAX_AGE_DAYS):
            return EmailProcessingResponse(
                success=False,
                email_id="",
                message=f"Email too old (received {email_date.date()}, max age: {settings.MAX_AGE_DAYS} days)",
                processing_time=time.time() - start_time
            )
        # Generate email ID
        email_id = str(uuid.uuid4())
        # Save parsed email to file
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
    max_age_days: Optional[int] = Query(settings.MAX_AGE_DAYS, description="Maximum age in days")
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
    """Get emails with optional filtering - defaults to substack.com only."""
    try:
        # Default to substack.com if no label specified
        if not label:
            label = "substack.com"
        
        # Get emails by label
        if label:
            emails = db.get_emails_by_label(label, max_age_days)
        else:
            emails = db.get_all_emails(max_age_days)
        
        # Apply date filtering if since parameter is provided
        if since:
            try:
                since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
                filtered_emails = []
                for email in emails:
                    if email.date >= since_date:
                        filtered_emails.append(email)
                emails = filtered_emails
            except ValueError:
                print(f"Invalid date format: {since}")
        
        return {
            "emails": emails,
            "total_count": len(emails),
            "label": label,
            "since": since,
            "max_age_days": max_age_days
        }
        
    except Exception as e:
        print(f"Error getting emails: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving emails: {str(e)}")

@app.post("/refresh", response_model=RefreshResponse)
async def refresh_emails():
    """Reprocess emails from maildir and refresh RAG index."""
    start_time = time.time()
    
    try:
        # TODO: Implement maildir reprocessing
        # This would scan the maildir directory and reprocess any unprocessed emails
        
        # Refresh RAG index
        pipeline = get_rag_pipeline()
        rag_success = pipeline.refresh_index()
        
        processing_time = time.time() - start_time
        
        return RefreshResponse(
            success=True,
            processed_count=0,
            errors=["Maildir reprocessing not yet implemented"] + ([] if rag_success else ["RAG index refresh failed"]),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return RefreshResponse(
            success=False,
            processed_count=0,
            errors=[f"Refresh failed: {str(e)}"],
            processing_time=processing_time
        )

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system with a question."""
    start_time = time.time()
    try:
        # Get sender from request if provided
        sender = getattr(request, 'sender', None)
        
        # Query the RAG pipeline
        result = get_rag_pipeline().query(
            question=request.question,
            label=request.label,
            sender=sender
        )
        
        # Convert context to metadata format
        metadata_list = []
        for doc_info in result.get('context', []):
            metadata = doc_info.get('metadata', {})
            metadata_list.append({
                'email_id': metadata.get('email_id'),
                'subject': metadata.get('subject', 'No Subject'),
                'sender': metadata.get('sender', 'Unknown'),
                'date': metadata.get('date', ''),
                'label': metadata.get('label', 'Unknown'),
                'parsed_path': metadata.get('source_file'),
                'has_attachments': metadata.get('has_attachments', False),
                'attachment_count': metadata.get('attachment_count', 0)
            })
        
        return QueryResponse(
            answer=result['answer'],
            context=result.get('context', []),
            metadata=metadata_list,
            processing_time=result.get('processing_time', 0)
        )
        
    except Exception as e:
        print(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/rag/stats")
async def get_rag_stats():
    """Get RAG pipeline statistics."""
    try:
        pipeline = get_rag_pipeline()
        stats = pipeline.get_pipeline_stats()
        return stats
    except Exception as e:
        print(f"Error getting RAG stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving RAG stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        pipeline = get_rag_pipeline()
        rag_status = "initialized" if pipeline.is_initialized else "not_initialized"
    except:
        rag_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db else "disconnected",
        "rag_pipeline": rag_status
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
        return prompt_manager.list_prompts()
    except Exception as e:
        print(f"Error getting prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompts: {str(e)}")

@app.get("/prompts/{prompt_type}")
async def get_prompt_template(prompt_type: str):
    """Get a specific prompt template."""
    try:
        from rag.prompts import prompt_manager, PromptType
        
        # Validate prompt type
        try:
            prompt_enum = PromptType(prompt_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid prompt type: {prompt_type}")
        
        # Get prompt template
        if prompt_type not in prompt_manager.prompts:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        template = prompt_manager.prompts[prompt_type]
        return {
            'name': template.name,
            'template': template.template,
            'description': template.description,
            'variables': template.variables,
            'version': template.version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompt template: {str(e)}")

@app.post("/prompts/{prompt_type}")
async def update_prompt_template(prompt_type: str, request: Dict[str, str]):
    """Update a prompt template."""
    try:
        from rag.prompts import prompt_manager, PromptType
        
        # Validate prompt type
        try:
            prompt_enum = PromptType(prompt_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid prompt type: {prompt_type}")
        
        # Validate request
        if 'template' not in request:
            raise HTTPException(status_code=400, detail="Template is required")
        
        # Update prompt
        prompt_manager.update_prompt(
            prompt_enum,
            new_template=request['template'],
            new_description=request.get('description'),
            new_version=request.get('version')
        )
        
        return {"message": f"Prompt {prompt_type} updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating prompt template: {str(e)}")

@app.get("/prompts/test/{prompt_type}")
async def test_prompt_template(prompt_type: str, request: Request):
    """Test a prompt template with provided variables."""
    try:
        from rag.prompts import prompt_manager, PromptType
        
        # Validate prompt type
        try:
            prompt_enum = PromptType(prompt_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid prompt type: {prompt_type}")
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        # Get formatted prompt
        formatted_prompt = prompt_manager.get_prompt(prompt_enum, **query_params)
        
        return {
            'prompt_type': prompt_type,
            'formatted_prompt': formatted_prompt,
            'variables_used': query_params
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error testing prompt template: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing prompt template: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics and performance metrics."""
    try:
        # Get RAG pipeline stats
        rag_stats = get_rag_pipeline().get_stats() if get_rag_pipeline() else {}
        
        # Get document counts
        email_files = list(Path("data/parsed_emails").glob("*.txt"))
        total_emails = len(email_files)
        
        # Get database stats
        db_stats = {}
        try:
            conn = get_db_connection()
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
        if Path("data/vector_store/faiss_index.bin").exists():
            vector_store_size = Path("data/vector_store/faiss_index.bin").stat().st_size
        
        parsed_emails_size = sum(f.stat().st_size for f in email_files)
        
        # Get memory usage
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate performance metrics
        performance_metrics = {
            'avg_query_time': rag_stats.get('avg_search_time', 0),
            'cache_hit_rate': (
                rag_stats.get('cache_hits', 0) / max(rag_stats.get('queries_processed', 1), 1) * 100
            ),
            'fallback_usage_rate': (
                rag_stats.get('fallback_used', 0) / max(rag_stats.get('queries_processed', 1), 1) * 100
            )
        }
        
        return {
            'system_status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'email_stats': {
                'total_emails': total_emails,
                'parsed_files_size_mb': round(parsed_emails_size / 1024 / 1024, 2),
                'vector_store_size_mb': round(vector_store_size / 1024 / 1024, 2)
            },
            'database_stats': db_stats,
            'rag_pipeline_stats': rag_stats,
            'performance_metrics': performance_metrics,
            'system_resources': {
                'memory_usage_mb': round(memory_usage, 2),
                'cpu_percent': psutil.cpu_percent(),
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        }
        
    except Exception as e:
        return {
            'system_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@app.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics for monitoring."""
    try:
        # Get RAG pipeline performance
        rag_stats = get_rag_pipeline().get_stats() if get_rag_pipeline() else {}
        
        # Calculate efficiency metrics
        total_queries = rag_stats.get('queries_processed', 0)
        cache_hits = rag_stats.get('cache_hits', 0)
        fallback_used = rag_stats.get('fallback_used', 0)
        
        efficiency_metrics = {
            'cache_efficiency': round(cache_hits / max(total_queries, 1) * 100, 2),
            'fallback_rate': round(fallback_used / max(total_queries, 1) * 100, 2),
            'avg_query_time_ms': round(rag_stats.get('avg_search_time', 0) * 1000, 2),
            'total_embeddings_generated': rag_stats.get('embeddings_generated', 0)
        }
        
        # Get embedding provider stats
        embedder_stats = {}
        if hasattr(get_rag_pipeline(), 'embedder') and get_rag_pipeline().embedder:
            embedder_stats = get_rag_pipeline().embedder.get_stats()
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'embedding_stats': embedder_stats,
            'rag_pipeline_stats': rag_stats,
            'recommendations': _get_performance_recommendations(efficiency_metrics, embedder_stats)
        }
        
    except Exception as e:
        return {'error': str(e)}

def _get_performance_recommendations(efficiency_metrics: dict, embedder_stats: dict) -> List[str]:
    """Generate performance recommendations based on metrics."""
    recommendations = []
    
    # Cache efficiency recommendations
    if efficiency_metrics['cache_efficiency'] < 20:
        recommendations.append("Consider increasing cache size for better performance")
    
    # Fallback rate recommendations
    if efficiency_metrics['fallback_rate'] > 10:
        recommendations.append("High fallback usage detected - check embedding provider status")
    
    # Query time recommendations
    if efficiency_metrics['avg_query_time_ms'] > 2000:
        recommendations.append("Query times are high - consider optimizing FAISS index")
    
    # Embedding provider recommendations
    if embedder_stats.get('fallback_used', 0) > 0:
        recommendations.append("Using fallback embedding provider - check primary provider")
    
    if not recommendations:
        recommendations.append("System performance is optimal")
    
    return recommendations

@app.post("/optimize")
async def optimize_system():
    """Run system optimization tasks."""
    try:
        optimizations = []
        
        # Clear caches
        if get_rag_pipeline():
            get_rag_pipeline().clear_cache()
            optimizations.append("Cleared RAG pipeline cache")
        
        # Optimize FAISS index if needed
        if hasattr(get_rag_pipeline(), 'retriever') and get_rag_pipeline().retriever:
            get_rag_pipeline().retriever.clear_cache()
            optimizations.append("Cleared FAISS retriever cache")
        
        # Check for index optimization opportunities
        if hasattr(get_rag_pipeline(), 'retriever') and get_rag_pipeline().retriever:
            index_stats = get_rag_pipeline().retriever.get_index_stats()
            if index_stats.get('total_documents', 0) > 1000:
                optimizations.append("Consider rebuilding FAISS index with IVF for better performance")
        
        return {
            'status': 'optimization_complete',
            'optimizations_applied': optimizations,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'optimization_failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "ingestion_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 