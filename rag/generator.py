import cohere
from typing import List, Dict, Any, Optional
from .config import settings
from .prompts import prompt_manager, PromptType

class LLMGenerator:
    """Generate responses using Cohere's generation API."""
    
    def __init__(self):
        self.client = None
        self.model = settings.GENERATION_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cohere client."""
        try:
            if settings.COHERE_API_KEY:
                self.client = cohere.Client(settings.COHERE_API_KEY)
                print(f"✅ Cohere generation client initialized with model: {self.model}")
            else:
                print("⚠️ COHERE_API_KEY not set. Generation will use fallback responses.")
                self.client = None
        except Exception as e:
            print(f"❌ Error initializing Cohere client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Cohere generation is available."""
        return self.client is not None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Cohere generation connection."""
        try:
            if not self.client:
                return {'status': 'error', 'message': 'Client not initialized'}
            
            # Test with a simple prompt
            response = self.client.generate(
                prompt="Hello, this is a test.",
                max_tokens=10,
                temperature=0.1,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return {'status': 'success', 'message': 'Connection successful'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], sender: str = None) -> str:
        """Generate response using centralized prompt management with proper citations."""
        if not self.is_available():
            return self._fallback_response(query, context_docs)
        
        try:
            # Get persona context if sender is provided
            persona_context = ""
            if sender:
                try:
                    from ingestion_api.persona_extractor import persona_extractor
                    persona_context = persona_extractor.get_persona_context(sender)
                except Exception as e:
                    print(f"Error getting persona context: {e}")
            
            # Build context with proper source attribution
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
            
            # Use centralized prompt management
            prompt = prompt_manager.get_rag_query_prompt(
                question=query,
                context_docs=context_docs,
                persona_context=persona_context
            )
            
            # Generate response
            response = self.client.generate(
                prompt=prompt,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._fallback_response(query, context_docs)
    
    def _fallback_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Fallback response when Cohere is not available."""
        # Use centralized fallback prompt
        fallback_prompt = prompt_manager.get_fallback_prompt(query, context_docs)
        
        # For fallback, we return the prompt text as-is since we don't have generation
        # In a real implementation, you might use a different LLM or template system
        return fallback_prompt
    
    def generate_email_summary(self, sender: str, subject: str, date: str, content: str) -> str:
        """Generate email summary using centralized prompts."""
        if not self.is_available():
            return f"Summary unavailable. Email from {sender}: {subject}"
        
        try:
            prompt = prompt_manager.get_email_summary_prompt(sender, subject, date, content)
            
            response = self.client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            print(f"Error generating email summary: {e}")
            return f"Summary unavailable. Email from {sender}: {subject}"
    
    def extract_topics(self, subject: str, content: str) -> List[str]:
        """Extract topics from email content using centralized prompts."""
        if not self.is_available():
            return []
        
        try:
            prompt = prompt_manager.get_topic_extraction_prompt(subject, content)
            
            response = self.client.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.1,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            # Parse the response to extract topics
            response_text = response.generations[0].text.strip()
            topics = [topic.strip() for topic in response_text.split(',') if topic.strip()]
            
            return topics
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []
    
    def analyze_sentiment(self, subject: str, content: str) -> Dict[str, str]:
        """Analyze sentiment using centralized prompts."""
        if not self.is_available():
            return {'sentiment': 'unknown', 'explanation': 'Analysis unavailable'}
        
        try:
            prompt = prompt_manager.get_sentiment_analysis_prompt(subject, content)
            
            response = self.client.generate(
                prompt=prompt,
                max_tokens=150,
                temperature=0.1,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            response_text = response.generations[0].text.strip()
            
            # Simple parsing of sentiment and explanation
            lines = response_text.split('\n')
            sentiment = 'neutral'
            explanation = response_text
            
            for line in lines:
                line_lower = line.lower()
                if 'positive' in line_lower:
                    sentiment = 'positive'
                elif 'negative' in line_lower:
                    sentiment = 'negative'
                elif 'neutral' in line_lower:
                    sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'explanation': explanation
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'sentiment': 'unknown', 'explanation': 'Analysis failed'}

    def derive_persona_traits(self, persona_name: str, context_docs: List[Dict]) -> str:
        """Derive persona traits and style from email chunks using the LLM."""
        if not self.is_available() or not context_docs:
            return "No specific style."
        try:
            # Concatenate up to 3 representative chunks
            sample_texts = []
            for doc in context_docs[:3]:
                content = doc.get('content', '')
                if content:
                    sample_texts.append(content)
            sample_text = '\n---\n'.join(sample_texts)
            prompt = (
                f"""Analyze the following email samples written by {persona_name}. "
                "Summarize their writing style, tone, and any common phrases or traits. "
                "Be concise.\n\nSamples:\n{sample_text}\n\nTraits:"""
            )
            prompt = prompt.format(persona_name=persona_name, sample_text=sample_text)
            response = self.client.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.2,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            return response.generations[0].text.strip()
        except Exception as e:
            print(f"Error deriving persona traits: {e}")
            return "No specific style."

    def generate_first_person_persona_response(self, persona_name: str, persona_traits: str, question: str, context_docs: List[Dict]) -> str:
        """Generate a first-person answer as the persona using derived traits with proper citations."""
        if not self.is_available():
            return f"I'm {persona_name}, but I can't answer right now."
        try:
            # Build context text with proper source attribution
            context_parts = []
            for i, doc_info in enumerate(context_docs, 1):
                metadata = doc_info.get('metadata', {})
                content = doc_info.get('content', '')
                sender_name = metadata.get('sender', 'Unknown')
                subject = metadata.get('subject', 'No Subject')
                
                context_parts.append(f"Source {i}: My email about {subject}")
                context_parts.append(f"Content: {content}")
                context_parts.append("---")
            
            context_text = "\n".join(context_parts)
            
            prompt = prompt_manager.get_prompt(
                PromptType.PERSONA_FIRST_PERSON_RESPONSE,
                persona_name=persona_name,
                persona_traits=persona_traits,
                question=question,
                context_text=context_text
            )
            
            response = self.client.generate(
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            print(f"Error generating first-person persona response: {e}")
            return f"I'm {persona_name}, but I can't answer right now."

# Global generator instance
generator = LLMGenerator() 