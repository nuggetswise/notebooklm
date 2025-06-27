"""
Minimal compatibility layer for JSON-based prompt system.
Loads prompts from JSON and provides backward-compatible method names.
"""

import json
import os
from typing import Dict, List, Any, Optional

class PromptManager:
    """Minimal prompt manager that loads from JSON and provides compatibility methods."""
    
    def __init__(self, prompts_file: str = "rag/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from JSON file."""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Prompts file {self.prompts_file} not found")
                return {"version": "1.0", "prompts": {}}
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return {"version": "1.0", "prompts": {}}
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by ID."""
        return self.prompts.get("prompts", {}).get(prompt_id)
    
    def get_prompt_template(self, prompt_id: str) -> Optional[str]:
        """Get the template for a specific prompt."""
        prompt = self.get_prompt(prompt_id)
        return prompt.get("template") if prompt else None
    
    def format_prompt(self, prompt_id: str, **kwargs) -> Optional[str]:
        """Format a prompt template with provided parameters."""
        template = self.get_prompt_template(prompt_id)
        if template:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                print(f"Missing parameter for prompt {prompt_id}: {e}")
                return None
        return None
    
    def list_prompts(self) -> Dict[str, str]:
        """List all available prompts with their descriptions."""
        return {
            prompt_id: prompt.get("description", "No description")
            for prompt_id, prompt in self.prompts.get("prompts", {}).items()
        }
    
    def get_prompt_info(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a prompt."""
        return self.get_prompt(prompt_id)
    
    # Compatibility methods for old code
    def get_rag_query_prompt(self, question: str, context_docs: List[Dict], persona_context: str = None) -> str:
        """Compatibility method for RAG query prompt."""
        # Build context text with proper source attribution
        context_parts = []
        for i, doc_info in enumerate(context_docs, 1):
            metadata = doc_info.get('metadata', {})
            content = doc_info.get('content', '')
            sender_name = metadata.get('sender', 'Unknown')
            subject = metadata.get('subject', 'No Subject')
            
            context_parts.append(f"Source {i}: Email from {sender_name} - {subject}")
            context_parts.append(f"Content: {content}")
            context_parts.append("---")
        
        context_text = "\n".join(context_parts)
        
        # Add persona context if provided
        if persona_context:
            context_text = f"Persona Context: {persona_context}\n\n{context_text}"
        
        return self.format_prompt("generation", query=question, context=context_text) or ""
    
    def get_fallback_prompt(self, query: str, context_docs: List[Dict]) -> str:
        """Compatibility method for fallback prompt."""
        if not context_docs:
            return f"I don't have enough information to answer your question: '{query}'. Please try rephrasing or check if there are relevant emails in the system."
        
        context_parts = []
        for doc_info in context_docs[:3]:  # Limit to 3 for fallback
            metadata = doc_info.get('metadata', {})
            subject = metadata.get('subject', 'Unknown')
            sender = metadata.get('sender', 'Unknown')
            context_parts.append(f"- Email from {sender}: {subject}")
        
        context_summary = "Relevant emails:\n" + "\n".join(context_parts)
        
        return f"I don't have enough information to answer your question: '{query}'.\n\n{context_summary}\n\nNote: This is a fallback response. For more detailed answers, please ensure the AI services are properly configured."
    
    def get_email_summary_prompt(self, sender: str, subject: str, date: str, content: str) -> str:
        """Compatibility method for email summary prompt."""
        return f"""Summarize this email in 1-2 sentences:

From: {sender}
Subject: {subject}
Date: {date}
Content: {content}

Summary:"""
    
    def get_topic_extraction_prompt(self, subject: str, content: str) -> str:
        """Compatibility method for topic extraction prompt."""
        return f"""Extract 3-5 main topics from this email content. Return as comma-separated list:

Subject: {subject}
Content: {content}

Topics:"""
    
    def get_sentiment_analysis_prompt(self, subject: str, content: str) -> str:
        """Compatibility method for sentiment analysis prompt."""
        return f"""Analyze the sentiment of this email:

Subject: {subject}
Content: {content}

Provide sentiment (positive/negative/neutral) and brief explanation:"""
    
    def get_persona_context_prompt(self, persona: Dict[str, Any]) -> str:
        """Compatibility method for persona context prompt."""
        if not persona:
            return ""
        
        name = persona.get('name', 'Unknown')
        topics = persona.get('topics', [])
        writing_style = persona.get('writing_style', '')
        
        topics_text = ", ".join(topics) if topics else "various topics"
        
        return f"""Context about {name}:
- Topics they write about: {topics_text}
- Writing style: {writing_style}
- Email count: {persona.get('email_count', 0)}"""

# Global prompt manager instance
prompt_manager = PromptManager()

# Convenience functions for backward compatibility
def get_retrieval_prompt(query: str) -> str:
    """Get formatted retrieval prompt."""
    return prompt_manager.format_prompt("retrieval", query=query) or ""

def get_generation_prompt(query: str, context: str) -> str:
    """Get formatted generation prompt."""
    return prompt_manager.format_prompt("generation", query=query, context=context) or ""

def get_prompt_template(prompt_id: str) -> Optional[str]:
    """Get raw prompt template."""
    return prompt_manager.get_prompt_template(prompt_id)

def list_available_prompts() -> Dict[str, str]:
    """List all available prompts."""
    return prompt_manager.list_prompts() 