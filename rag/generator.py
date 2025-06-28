import cohere
import groq
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from .config import settings

class MultiProviderGenerator:
    """Generate responses using multiple LLM providers with fallback chain."""
    
    def __init__(self):
        self.cohere_client = None
        self.groq_client = None
        self.gemini_client = None
        self.current_provider = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all available LLM clients."""
        # Initialize Cohere
        try:
            if settings.COHERE_API_KEY:
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
                print(f"✅ Cohere client initialized")
            else:
                print("⚠️ COHERE_API_KEY not set")
        except Exception as e:
            print(f"❌ Error initializing Cohere client: {e}")
        
        # Initialize Groq
        try:
            if hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY:
                self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
                print(f"✅ Groq client initialized")
            else:
                print("⚠️ GROQ_API_KEY not set")
        except Exception as e:
            print(f"❌ Error initializing Groq client: {e}")
        
        # Initialize Gemini
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
                print(f"✅ Gemini client initialized")
            else:
                print("⚠️ GEMINI_API_KEY not set")
        except Exception as e:
            print(f"❌ Error initializing Gemini client: {e}")
        
        # Groq models (in order of preference)
        self.groq_models = [
            "gemma2-9b-it"  # Only using Gemma model
        ]
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        return any([self.cohere_client, self.groq_client, self.gemini_client])
    
    def _try_cohere(self, prompt: str, max_tokens: int = None, temperature: float = 0.7) -> Optional[str]:
        """Try to generate response using Cohere."""
        if not self.cohere_client:
            return None
        
        # Use provider-specific token limit
        if max_tokens is None:
            max_tokens = min(settings.MAX_TOKENS, settings.COHERE_MAX_TOKENS)
        
        try:
            # Check prompt length and truncate if needed
            estimated_tokens = len(prompt.split()) * 1.3  # Rough estimation
            if estimated_tokens > settings.COHERE_MAX_TOKENS:
                print(f"⚠️ Cohere prompt too long ({estimated_tokens:.0f} tokens), truncating...")
                # Truncate prompt to fit within limits
                words = prompt.split()
                max_words = int(settings.COHERE_MAX_TOKENS / 1.3)
                prompt = " ".join(words[:max_words])
            # Final check: if still too long, hard truncate
            while len(prompt.split()) * 1.3 > settings.COHERE_MAX_TOKENS:
                prompt = " ".join(prompt.split()[:-10])
            
            # Use the correct Cohere API parameters (no 'model' param for generate)
            response = self.cohere_client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            self.current_provider = "cohere"
            return response.generations[0].text.strip()
        except Exception as e:
            print(f"Cohere generation failed: {e}")
            return None
    
    def _try_groq(self, prompt: str, max_tokens: int = None, temperature: float = 0.7) -> Optional[str]:
        """Try to generate response using Groq."""
        if not self.groq_client:
            return None
        
        # Use provider-specific token limit
        if max_tokens is None:
            max_tokens = min(settings.MAX_TOKENS, settings.GROQ_MAX_TOKENS)
        
        try:
            # Check prompt length and truncate if needed
            estimated_tokens = len(prompt.split()) * 1.3  # Rough estimation
            if estimated_tokens > settings.GROQ_MAX_TOKENS:
                print(f"⚠️ Groq prompt too long ({estimated_tokens:.0f} tokens), truncating...")
                # Truncate prompt to fit within limits
                words = prompt.split()
                max_words = int(settings.GROQ_MAX_TOKENS / 1.3)
                prompt = " ".join(words[:max_words])
            
            # Try different Groq models in order of preference
            models = [
                "gemma2-9b-it",  # Primary: Gemma2 9B
                "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout
                "llama-3.3-70b-versatile",  # Llama 3.3 70B
                "llama3-8b-8192"  # Fallback
            ]
            
            for model in models:
                try:
                    response = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=1,
                        stream=False
                    )
                    self.current_provider = f"groq-{model}"
                    return response.choices[0].message.content.strip()
                except Exception as model_error:
                    print(f"Groq model {model} failed: {model_error}")
                    continue
            
            print("All Groq models failed")
            return None
            
        except Exception as e:
            print(f"Groq generation failed: {e}")
            return None
    
    def _try_gemini(self, prompt: str, max_tokens: int = None, temperature: float = 0.7) -> Optional[str]:
        """Try to generate response using Gemini."""
        if not self.gemini_client:
            return None
        
        # Use provider-specific token limit
        if max_tokens is None:
            max_tokens = min(settings.MAX_TOKENS, settings.GEMINI_MAX_TOKENS)
        
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            self.current_provider = "gemini"
            return response.text.strip()
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return None
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], sender: str = None) -> Dict[str, Any]:
        """Generate response using fallback chain: Groq → Gemini → Cohere."""
        if not self.is_available():
            fallback_response = self._fallback_response(query, context_docs)
            return {
                "response": fallback_response,
                "provider": "fallback",
                "model": "none"
            }
        
        try:
            # Import prompt manager here to avoid circular imports
            from .prompts import prompt_manager
            
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
                
                # Handle different metadata structures safely
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
            
            # Try providers in new fallback order: Groq → Gemini → Cohere
            response = None
            provider_info = "unknown"
            
            # Try Groq first (primary)
            response = self._try_groq(prompt, settings.MAX_TOKENS, settings.TEMPERATURE)
            if response:
                print(f"✅ Generated response using Groq")
                return {
                    "response": response,
                    "provider": "groq",
                    "model": self.current_provider.replace("groq-", "")
                }
            
            # Try Gemini second
            response = self._try_gemini(prompt, settings.MAX_TOKENS, settings.TEMPERATURE)
            if response:
                print(f"✅ Generated response using Gemini")
                return {
                    "response": response,
                    "provider": "gemini",
                    "model": "gemini-2.0-flash"
                }
            
            # Try Cohere third (last resort)
            response = self._try_cohere(prompt, settings.MAX_TOKENS, settings.TEMPERATURE)
            if response:
                print(f"✅ Generated response using Cohere")
                provider_info = "cohere"
                return {
                    "response": response,
                    "provider": provider_info,
                    "model": "command"
                }
            
            # If all providers fail, use fallback
            print("❌ All LLM providers failed, using fallback response")
            fallback_response = self._fallback_response(query, context_docs)
            return {
                "response": fallback_response,
                "provider": "fallback",
                "model": "none"
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            fallback_response = self._fallback_response(query, context_docs)
            return {
                "response": fallback_response,
                "provider": "error",
                "model": "none"
            }
    
    def _fallback_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Fallback response when all LLM providers are unavailable."""
        try:
            # Import prompt manager here to avoid circular imports
            from .prompts import prompt_manager
            # Use centralized fallback prompt
            fallback_prompt = prompt_manager.get_fallback_prompt(query, context_docs)
            
            # For fallback, we return the prompt text as-is since we don't have generation
            return fallback_prompt
        except Exception as e:
            print(f"Error in fallback response: {e}")
            return f"I don't have information about that."
    
    def generate_email_summary(self, sender: str, subject: str, date: str, content: str) -> str:
        """Generate email summary using fallback chain."""
        if not self.is_available():
            return f"Summary unavailable. Email from {sender}: {subject}"
        
        try:
            # Import prompt manager here to avoid circular imports
            from .prompts import prompt_manager
            prompt = prompt_manager.get_email_summary_prompt(sender, subject, date, content)
            
            # Try providers in fallback order
            response = self._try_cohere(prompt, 200, 0.3)
            if response:
                return response
            
            response = self._try_groq(prompt, 200, 0.3)
            if response:
                return response
            
            response = self._try_gemini(prompt, 200, 0.3)
            if response:
                return response
            
            return f"Summary unavailable. Email from {sender}: {subject}"
            
        except Exception as e:
            print(f"Error generating email summary: {e}")
            return f"Summary unavailable. Email from {sender}: {subject}"
    
    def extract_topics(self, subject: str, content: str) -> List[str]:
        """Extract topics using fallback chain."""
        if not self.is_available():
            return []
        
        try:
            # Import prompt manager here to avoid circular imports
            from .prompts import prompt_manager
            prompt = prompt_manager.get_topic_extraction_prompt(subject, content)
            
            # Try providers in fallback order
            response = self._try_cohere(prompt, 100, 0.1)
            if response:
                topics = [topic.strip() for topic in response.split(',') if topic.strip()]
                return topics
            
            response = self._try_groq(prompt, 100, 0.1)
            if response:
                topics = [topic.strip() for topic in response.split(',') if topic.strip()]
                return topics
            
            response = self._try_gemini(prompt, 100, 0.1)
            if response:
                topics = [topic.strip() for topic in response.split(',') if topic.strip()]
                return topics
            
            return []
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []
    
    def analyze_sentiment(self, subject: str, content: str) -> Dict[str, str]:
        """Analyze sentiment using fallback chain."""
        if not self.is_available():
            return {'sentiment': 'unknown', 'explanation': 'Analysis unavailable'}
        
        try:
            # Import prompt manager here to avoid circular imports
            from .prompts import prompt_manager
            prompt = prompt_manager.get_sentiment_analysis_prompt(subject, content)
            
            # Try providers in fallback order
            response = self._try_cohere(prompt, 150, 0.1)
            if response:
                return self._parse_sentiment(response)
            
            response = self._try_groq(prompt, 150, 0.1)
            if response:
                return self._parse_sentiment(response)
            
            response = self._try_gemini(prompt, 150, 0.1)
            if response:
                return self._parse_sentiment(response)
            
            return {'sentiment': 'unknown', 'explanation': 'Analysis failed'}
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'sentiment': 'unknown', 'explanation': 'Analysis failed'}
    
    def _parse_sentiment(self, response_text: str) -> Dict[str, str]:
        """Parse sentiment from response text."""
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
    
    def get_current_provider(self) -> str:
        """Get the current provider being used."""
        return self.current_provider or "none"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connections to all providers."""
        results = {}
        
        # Test Cohere
        if self.cohere_client:
            try:
                response = self._try_cohere("Hello, this is a test.", 10, 0.1)
                results['cohere'] = {'status': 'success', 'response': response[:50] + '...' if response else 'No response'}
            except Exception as e:
                results['cohere'] = {'status': 'error', 'message': str(e)}
        else:
            results['cohere'] = {'status': 'not_configured'}
        
        # Test Groq
        if self.groq_client:
            try:
                response = self._try_groq("Hello, this is a test.", 10, 0.1)
                results['groq'] = {'status': 'success', 'response': response[:50] + '...' if response else 'No response'}
            except Exception as e:
                results['groq'] = {'status': 'error', 'message': str(e)}
        else:
            results['groq'] = {'status': 'not_configured'}
        
        # Test Gemini
        if self.gemini_client:
            try:
                response = self._try_gemini("Hello, this is a test.", 10, 0.1)
                results['gemini'] = {'status': 'success', 'response': response[:50] + '...' if response else 'No response'}
            except Exception as e:
                results['gemini'] = {'status': 'error', 'message': str(e)}
        else:
            results['gemini'] = {'status': 'not_configured'}
        
        return results

# Global generator instance
generator = MultiProviderGenerator() 