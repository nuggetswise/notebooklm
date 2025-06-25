"""
Centralized Prompt Management System for Email RAG

This module contains all prompts used throughout the RAG system,
making them easy to maintain, version, and customize.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    """Types of prompts used in the system."""
    RAG_QUERY = "rag_query"
    RAG_QUERY_WITH_PERSONA = "rag_query_with_persona"
    PERSONA_CONTEXT = "persona_context"
    FALLBACK_RESPONSE = "fallback_response"
    EMAIL_SUMMARY = "email_summary"
    TOPIC_EXTRACTION = "topic_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PERSONA_FIRST_PERSON_RESPONSE = "persona_first_person_response"

@dataclass
class PromptTemplate:
    """A prompt template with variables."""
    name: str
    template: str
    description: str
    variables: List[str]
    version: str = "1.0"

class PromptManager:
    """Centralized prompt management system."""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
        self.system_personality = self._get_system_personality()
    
    def _get_system_personality(self) -> str:
        """Define the system's personality and behavior."""
        return """You are an intelligent email assistant that helps users understand and interact with their email content. 
You are helpful, accurate, and provide context-aware responses based on the email data available.
You always ground your responses in the actual email content provided and cite specific sources when possible."""
    
    def _initialize_prompts(self) -> Dict[str, PromptTemplate]:
        """Initialize all prompt templates."""
        return {
            PromptType.RAG_QUERY.value: PromptTemplate(
                name="Basic RAG Query",
                template="""You are an intelligent email assistant that provides accurate, grounded answers based on email content. 

IMPORTANT: 
- Only answer based on the provided email content
- Always cite specific sources when making claims
- If the information is not in the provided content, say "I don't have information about that in the provided emails"
- Provide citations in the format: [Source: Email from {sender} - {subject}]

Question: {question}

Email content:
{context_text}

Instructions:
1. Answer the question based ONLY on the provided email content
2. Include specific citations for any claims or information
3. If you cannot answer from the provided content, clearly state this
4. Be concise but thorough

Answer:""",
                description="Basic RAG query with citation requirements",
                variables=["question", "context_text"],
                version="2.0"
            ),
            
            PromptType.RAG_QUERY_WITH_PERSONA.value: PromptTemplate(
                name="RAG Query with Persona Context",
                template="""You are an intelligent email assistant that provides accurate, grounded answers based on email content.

IMPORTANT: 
- Only answer based on the provided email content
- Always cite specific sources when making claims
- If the information is not in the provided content, say "I don't have information about that in the provided emails"
- Provide citations in the format: [Source: Email from {sender} - {subject}]

Context about the email sender: {persona_context}

Question: {question}

Email content:
{context_text}

Instructions:
1. Answer the question based ONLY on the provided email content
2. Include specific citations for any claims or information
3. If you cannot answer from the provided content, clearly state this
4. Consider the sender's context when relevant
5. Be concise but thorough

Answer:""",
                description="RAG query with persona context and citation requirements",
                variables=["persona_context", "question", "context_text"],
                version="2.0"
            ),
            
            PromptType.PERSONA_CONTEXT.value: PromptTemplate(
                name="Persona Context Generation",
                template="""This email is from {first_name} ({sender}).

{email_count_text}

{topics_text}

{labels_text}""",
                description="Generate contextual information about a sender",
                variables=["first_name", "sender", "email_count_text", "topics_text", "labels_text"],
                version="1.0"
            ),
            
            PromptType.FALLBACK_RESPONSE.value: PromptTemplate(
                name="Fallback Response",
                template="""I don't have enough information to answer your question: '{question}'. 

{context_summary}

Note: This is a fallback response. For more detailed answers, please ensure the AI services are properly configured.""",
                description="Fallback response when AI services are unavailable",
                variables=["question", "context_summary"],
                version="1.0"
            ),
            
            PromptType.EMAIL_SUMMARY.value: PromptTemplate(
                name="Email Summary",
                template="""Please provide a concise summary of this email:

From: {sender}
Subject: {subject}
Date: {date}

Content:
{content}

Summary:""",
                description="Generate a summary of email content",
                variables=["sender", "subject", "date", "content"],
                version="1.0"
            ),
            
            PromptType.TOPIC_EXTRACTION.value: PromptTemplate(
                name="Topic Extraction",
                template="""Analyze the following email content and identify the main topics discussed:

Subject: {subject}
Content: {content}

Topics to look for:
- AI: artificial intelligence, machine learning, GPT, LLM, neural networks
- Tech: technology, software, programming, coding, development, startup
- Business: business, entrepreneur, startup, company, market, investment
- Finance: finance, financial, money, investment, trading, crypto
- Health: health, medical, wellness, fitness, nutrition
- News: news, update, announcement, breaking, latest
- Education: education, learning, course, training, tutorial
- Marketing: marketing, advertising, promotion, campaign, growth

Identify the most relevant topics (comma-separated):""",
                description="Extract topics from email content",
                variables=["subject", "content"],
                version="1.0"
            ),
            
            PromptType.SENTIMENT_ANALYSIS.value: PromptTemplate(
                name="Sentiment Analysis",
                template="""Analyze the sentiment of this email:

Subject: {subject}
Content: {content}

Provide a sentiment analysis (positive/neutral/negative) and brief explanation:""",
                description="Analyze the sentiment of email content",
                variables=["subject", "content"],
                version="1.0"
            ),
            
            PromptType.PERSONA_FIRST_PERSON_RESPONSE.value: PromptTemplate(
                name="Persona First Person Response",
                template="""You are {persona_name}. Based on your writing style and the emails you've sent, respond to this question in your own voice, as if you're having a conversation with the person asking.

IMPORTANT: 
- Only answer based on the provided email content
- Always cite specific sources when making claims
- If the information is not in the provided content, say "I don't have information about that in my emails"
- Provide citations in the format: [Source: My email about this topic]

Your typical style: {persona_traits}

Question: {question}

Relevant context from your emails:
{context_text}

Instructions:
1. Answer in your natural, conversational voice
2. Base your response ONLY on the provided email content
3. Include specific citations for any claims or information
4. If you cannot answer from the provided content, clearly state this
5. Be engaging and personality-driven

Your response:""",
                description="Generate a natural first-person answer as the persona with citations",
                variables=["persona_name", "persona_traits", "question", "context_text"],
                version="2.0"
            ),
        }
    
    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """Get a formatted prompt for the given type."""
        if prompt_type.value not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = self.prompts[prompt_type.value]
        
        # Validate required variables
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables for {prompt_type.value}: {missing_vars}")
        
        return template.template.format(**kwargs)
    
    def get_rag_query_prompt(self, question: str, context_docs: List[Dict], persona_context: str = None) -> str:
        """Get the appropriate RAG query prompt based on available context."""
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
        
        if persona_context:
            return self.get_prompt(
                PromptType.RAG_QUERY_WITH_PERSONA,
                persona_context=persona_context,
                question=question,
                context_text=context_text
            )
        else:
            return self.get_prompt(
                PromptType.RAG_QUERY,
                question=question,
                context_text=context_text
            )
    
    def get_persona_context_prompt(self, persona: Dict) -> str:
        """Generate persona context prompt."""
        first_name = persona.get('first_name', 'Unknown')
        sender = persona.get('sender', 'Unknown')
        
        # Email count text
        email_count = persona.get('email_count', 0)
        if email_count > 1:
            email_count_text = f"They have sent {email_count} emails before."
        else:
            email_count_text = "This is their first email."
        
        # Topics text
        topics = persona.get('topics', [])
        if topics:
            topics_str = ', '.join(topics)
            topics_text = f"They typically write about: {topics_str}."
        else:
            topics_text = ""
        
        # Labels text
        labels = persona.get('labels', [])
        if labels:
            labels_str = ', '.join(labels)
            labels_text = f"Common labels: {labels_str}."
        else:
            labels_text = ""
        
        return self.get_prompt(
            PromptType.PERSONA_CONTEXT,
            first_name=first_name,
            sender=sender,
            email_count_text=email_count_text,
            topics_text=topics_text,
            labels_text=labels_text
        )
    
    def get_fallback_prompt(self, question: str, context_docs: List[Dict]) -> str:
        """Get fallback response prompt."""
        if not context_docs:
            context_summary = "Please try rephrasing or check if there are relevant emails in the system."
        else:
            context_parts = []
            for doc_info in context_docs[:3]:  # Limit to 3 for fallback
                metadata = doc_info.get('metadata', {})
                subject = metadata.get('subject', 'Unknown')
                sender = metadata.get('sender', 'Unknown')
                context_parts.append(f"- Email from {sender}: {subject}")
            
            context_summary = "Relevant emails:\n" + "\n".join(context_parts)
        
        return self.get_prompt(
            PromptType.FALLBACK_RESPONSE,
            question=question,
            context_summary=context_summary
        )
    
    def get_email_summary_prompt(self, sender: str, subject: str, date: str, content: str) -> str:
        """Get email summary prompt."""
        return self.get_prompt(
            PromptType.EMAIL_SUMMARY,
            sender=sender,
            subject=subject,
            date=date,
            content=content
        )
    
    def get_topic_extraction_prompt(self, subject: str, content: str) -> str:
        """Get topic extraction prompt."""
        return self.get_prompt(
            PromptType.TOPIC_EXTRACTION,
            subject=subject,
            content=content
        )
    
    def get_sentiment_analysis_prompt(self, subject: str, content: str) -> str:
        """Get sentiment analysis prompt."""
        return self.get_prompt(
            PromptType.SENTIMENT_ANALYSIS,
            subject=subject,
            content=content
        )
    
    def list_prompts(self) -> Dict[str, Dict]:
        """List all available prompts with their metadata."""
        return {
            prompt_type: {
                'name': template.name,
                'description': template.description,
                'variables': template.variables,
                'version': template.version
            }
            for prompt_type, template in self.prompts.items()
        }
    
    def update_prompt(self, prompt_type: PromptType, new_template: str, new_description: str = None, new_version: str = None):
        """Update a prompt template."""
        if prompt_type.value not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = self.prompts[prompt_type.value]
        template.template = new_template
        if new_description:
            template.description = new_description
        if new_version:
            template.version = new_version
    
    def add_prompt(self, prompt_type: str, template: PromptTemplate):
        """Add a new prompt template."""
        self.prompts[prompt_type] = template

# Global prompt manager instance
prompt_manager = PromptManager() 