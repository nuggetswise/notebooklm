import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import email.utils
from email.header import decode_header

# Import centralized prompt system
try:
    from rag.prompts import prompt_manager
    PROMPT_SYSTEM_AVAILABLE = True
except ImportError:
    PROMPT_SYSTEM_AVAILABLE = False
    print("Warning: Centralized prompt system not available. Using fallback topic detection.")

class PersonaExtractor:
    """Extract personas from email senders and create personalized profiles."""
    
    def __init__(self):
        self.personas_file = Path("data/personas.json")
        self.personas_file.parent.mkdir(exist_ok=True)
        self.personas = self._load_personas()
        
        # Common name patterns and variations
        self.name_patterns = [
            r'^([A-Z][a-z]+)',  # First word starting with capital
            r'([A-Z][a-z]+)\s+',  # Word starting with capital followed by space
            r'^([A-Z][a-z]+)\s+[A-Z]',  # First word + space + capital letter
            r'([A-Z][a-z]+)\s+from\s+',  # Name + "from"
            r'([A-Z][a-z]+)\s+via\s+',  # Name + "via"
            r'([A-Z][a-z]+)\s+<',  # Name + "<"
        ]
        
        # Common prefixes to skip
        self.skip_prefixes = [
            'newsletter', 'noreply', 'no-reply', 'donotreply', 'do-not-reply',
            'support', 'info', 'admin', 'contact', 'hello', 'team'
        ]
        
        # Common suffixes to skip
        self.skip_suffixes = [
            'newsletter', 'team', 'support', 'info', 'admin'
        ]
        
        # Fallback topic keywords (used when prompt system is not available)
        self.fallback_topics_keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'gpt', 'llm', 'neural'],
            'Tech': ['technology', 'software', 'programming', 'coding', 'development', 'startup'],
            'Business': ['business', 'entrepreneur', 'startup', 'company', 'market', 'investment'],
            'Finance': ['finance', 'financial', 'money', 'investment', 'trading', 'crypto'],
            'Health': ['health', 'medical', 'wellness', 'fitness', 'nutrition'],
            'News': ['news', 'update', 'announcement', 'breaking', 'latest'],
            'Education': ['education', 'learning', 'course', 'training', 'tutorial'],
            'Marketing': ['marketing', 'advertising', 'promotion', 'campaign', 'growth']
        }
    
    def _load_personas(self) -> Dict[str, Dict]:
        """Load existing personas from file."""
        if self.personas_file.exists():
            try:
                with open(self.personas_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading personas: {e}")
        return {}
    
    def _save_personas(self):
        """Save personas to file."""
        try:
            with open(self.personas_file, 'w', encoding='utf-8') as f:
                json.dump(self.personas, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving personas: {e}")
    
    def extract_first_name(self, sender: str) -> Optional[str]:
        """Extract first name from email sender string."""
        if not sender:
            return None
        
        # Clean the sender string
        sender_clean = sender.strip()
        
        # Try to parse as email address with display name
        try:
            # Parse email address
            parsed = email.utils.parseaddr(sender_clean)
            display_name, email_addr = parsed
            
            # If we have a display name, try to extract first name from it
            if display_name and display_name != email_addr:
                first_name = self._extract_name_from_display(display_name)
                if first_name:
                    return first_name
            
            # If no display name or extraction failed, try email address
            if email_addr:
                first_name = self._extract_name_from_email(email_addr)
                if first_name:
                    return first_name
                    
        except Exception:
            pass
        
        # Fallback: try direct extraction from sender string
        return self._extract_name_from_display(sender_clean)
    
    def _extract_name_from_display(self, display_name: str) -> Optional[str]:
        """Extract first name from display name."""
        if not display_name:
            return None
        
        # Decode header if needed
        try:
            decoded_name = decode_header(display_name)[0][0]
            if isinstance(decoded_name, bytes):
                display_name = decoded_name.decode('utf-8', errors='ignore')
            else:
                display_name = str(decoded_name)
        except Exception:
            pass
        
        # Try different patterns
        for pattern in self.name_patterns:
            match = re.search(pattern, display_name)
            if match:
                name = match.group(1).strip()
                if self._is_valid_name(name):
                    return name
        
        # Try splitting by common separators
        separators = [' ', ',', '|', '-', '_', '.']
        for sep in separators:
            if sep in display_name:
                parts = display_name.split(sep)
                for part in parts:
                    part = part.strip()
                    if self._is_valid_name(part):
                        return part
        
        return None
    
    def _extract_name_from_email(self, email_addr: str) -> Optional[str]:
        """Extract first name from email address."""
        if not email_addr or '@' not in email_addr:
            return None
        
        # Get the local part (before @)
        local_part = email_addr.split('@')[0]
        
        # Remove common prefixes and suffixes
        for prefix in self.skip_prefixes:
            if local_part.lower().startswith(prefix.lower()):
                local_part = local_part[len(prefix):]
        
        for suffix in self.skip_suffixes:
            if local_part.lower().endswith(suffix.lower()):
                local_part = local_part[:-len(suffix)]
        
        # Try to extract name from remaining part
        separators = ['.', '_', '-']
        for sep in separators:
            if sep in local_part:
                parts = local_part.split(sep)
                for part in parts:
                    part = part.strip()
                    if self._is_valid_name(part):
                        return part
        
        # If no separators, check if the whole local part looks like a name
        if self._is_valid_name(local_part):
            return local_part
        
        return None
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if a string looks like a valid first name."""
        if not name or len(name) < 2:
            return False
        
        # Must start with a letter and contain only letters
        if not re.match(r'^[A-Za-z]+$', name):
            return False
        
        # Must be at least 2 characters
        if len(name) < 2:
            return False
        
        # Must not be too long (likely not a name if > 20 chars)
        if len(name) > 20:
            return False
        
        # Must not be in skip lists
        if name.lower() in [p.lower() for p in self.skip_prefixes + self.skip_suffixes]:
            return False
        
        return True
    
    def create_persona(self, sender: str, subject: str = "", content: str = "") -> Dict[str, any]:
        """Create or update a persona for a sender."""
        first_name = self.extract_first_name(sender)
        
        if not first_name:
            # Create a generic persona for unknown senders
            persona_id = f"unknown_{hash(sender) % 10000}"
            persona = {
                'id': persona_id,
                'sender': sender,
                'first_name': 'Unknown',
                'display_name': sender,
                'email_count': 1,
                'first_seen': datetime.utcnow().isoformat(),
                'last_seen': datetime.utcnow().isoformat(),
                'topics': [],
                'labels': [],
                'persona_type': 'unknown'
            }
        else:
            # Create or update persona for known sender
            persona_id = f"{first_name.lower()}_{hash(sender) % 10000}"
            
            if persona_id in self.personas:
                # Update existing persona
                persona = self.personas[persona_id]
                persona['email_count'] += 1
                persona['last_seen'] = datetime.utcnow().isoformat()
            else:
                # Create new persona
                persona = {
                    'id': persona_id,
                    'sender': sender,
                    'first_name': first_name,
                    'display_name': sender,
                    'email_count': 1,
                    'first_seen': datetime.utcnow().isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'topics': [],
                    'labels': [],
                    'persona_type': 'individual'
                }
        
        # Update topics and labels if provided
        if subject or content:
            self._update_persona_topics(persona, subject, content)
        
        # Save persona
        self.personas[persona_id] = persona
        self._save_personas()
        
        return persona
    
    def _update_persona_topics(self, persona: Dict, subject: str = "", content: str = ""):
        """Update persona topics based on email content using centralized prompts."""
        combined_text = f"{subject} {content}".lower()
        
        if PROMPT_SYSTEM_AVAILABLE:
            # Use centralized prompt system for topic extraction
            try:
                from rag.generator import generator
                topics = generator.extract_topics(subject, content)
                if topics:
                    # Update persona topics
                    for topic in topics:
                        if topic not in persona['topics']:
                            persona['topics'].append(topic)
                    return
            except Exception as e:
                print(f"Error using centralized topic extraction: {e}")
        
        # Fallback to keyword-based topic detection
        found_topics = []
        for topic, keywords in self.fallback_topics_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    found_topics.append(topic)
                    break
        
        # Update persona topics
        for topic in found_topics:
            if topic not in persona['topics']:
                persona['topics'].append(topic)
    
    def get_persona(self, sender: str) -> Optional[Dict]:
        """Get persona for a sender."""
        first_name = self.extract_first_name(sender)
        if not first_name:
            return None
        
        persona_id = f"{first_name.lower()}_{hash(sender) % 10000}"
        return self.personas.get(persona_id)
    
    def get_all_personas(self) -> List[Dict]:
        """Get all personas."""
        return list(self.personas.values())
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Dict]:
        """Get persona by ID."""
        return self.personas.get(persona_id)
    
    def get_persona_context(self, sender: str) -> str:
        """Get contextual information about a sender for RAG queries."""
        persona = self.get_persona(sender)
        if not persona:
            return f"This email is from {sender}."
        
        # Use centralized prompt system if available
        if PROMPT_SYSTEM_AVAILABLE:
            try:
                return prompt_manager.get_persona_context_prompt(persona)
            except Exception as e:
                print(f"Error using centralized persona context: {e}")
        
        # Fallback to manual context generation
        context_parts = [f"This email is from {persona['first_name']} ({persona['sender']})."]
        
        if persona['email_count'] > 1:
            context_parts.append(f"They have sent {persona['email_count']} emails before.")
        
        if persona['topics']:
            topics_str = ', '.join(persona['topics'])
            context_parts.append(f"They typically write about: {topics_str}.")
        
        if persona['labels']:
            labels_str = ', '.join(persona['labels'])
            context_parts.append(f"Common labels: {labels_str}.")
        
        return ' '.join(context_parts)
    
    def update_persona_label(self, sender: str, label: str):
        """Update persona with a new label."""
        persona = self.get_persona(sender)
        if persona and label not in persona['labels']:
            persona['labels'].append(label)
            self._save_personas()

# Global instance
persona_extractor = PersonaExtractor() 