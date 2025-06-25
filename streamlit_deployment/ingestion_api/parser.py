import email
import re
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from email import policy
from email.parser import BytesParser
import base64

# Open Notebook imports
try:
    from open_notebook.domain import models, notebook
    OPEN_NOTEBOOK_AVAILABLE = True
    print("✅ Open-notebook imported successfully")
except ImportError as e:
    OPEN_NOTEBOOK_AVAILABLE = False
    print(f"Warning: open-notebook not available. Notebook creation will be skipped. Error: {e}")
except Exception as e:
    OPEN_NOTEBOOK_AVAILABLE = False
    print(f"Warning: open-notebook database not configured. Notebook creation will be skipped. Error: {e}")

# Document processing imports
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    # Try to import pytesseract without pandas dependency
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except (ImportError, ValueError) as e:
    TESSERACT_AVAILABLE = False
    print(f"Warning: pytesseract not available. OCR will be skipped. Error: {e}")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

from .config import settings
from .persona_extractor import persona_extractor


def clean_email_address(email_str):
    """Clean email address to handle special characters."""
    if not email_str:
        return None
    
    # Remove angle brackets if present
    email_str = email_str.strip()
    if email_str.startswith('<') and email_str.endswith('>'):
        email_str = email_str[1:-1]
    
    # Extract email from "Display Name <email@domain.com>" format
    if '<' in email_str and '>' in email_str:
        start = email_str.rfind('<') + 1
        end = email_str.rfind('>')
        if start < end:
            email_str = email_str[start:end]
    
    # Clean up any remaining special characters
    email_str = email_str.strip()
    
    # Basic email validation
    if '@' in email_str and '.' in email_str.split('@')[1]:
        return email_str
    
    return None

class EmailParser:
    """Parse MIME emails and extract content from attachments."""
    
    def __init__(self):
        self.parser = BytesParser(policy=policy.default)
    
    def parse_email(self, raw_email: bytes) -> Dict[str, Any]:
        """Parse raw MIME email and extract all content."""
        try:
            # Parse the email
            msg = self.parser.parsebytes(raw_email)
            
            # Extract basic metadata
            subject = msg.get('subject', 'No Subject')
            sender = msg.get('from', 'unknown@example.com')
            date_str = msg.get('date')
            date = self._parse_date(date_str) if date_str else datetime.utcnow()
            
            # Extract sender domain as label
            match = re.search(r'@([A-Za-z0-9.-]+)', sender)
            domain_label = match.group(1).lower() if match else "unknown"
            label = domain_label
            
            # Extract body content
            body = self._extract_body(msg)
            
            # Process attachments
            attachments = self._process_attachments(msg)
            
            # Combine all text content
            full_content = self._combine_content(body, attachments)
            
            # Extract persona information
            persona = persona_extractor.create_persona(sender, subject, full_content)
            
            return {
                'subject': subject,
                'sender': sender,
                'date': date,
                'label': label,
                'body': body,
                'attachments': attachments,
                'full_content': full_content,
                'has_attachments': len(attachments) > 0,
                'attachment_count': len(attachments),
                'persona': persona
            }
            
        except Exception as e:
            print(f"Error parsing email: {e}")
            return {
                'subject': 'Error parsing email',
                'sender': 'unknown@example.com',
                'date': datetime.utcnow(),
                'label': 'unknown',
                'body': f'Error parsing email: {str(e)}',
                'attachments': [],
                'full_content': f'Error parsing email: {str(e)}',
                'has_attachments': False,
                'attachment_count': 0,
                'persona': None
            }
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime object."""
        try:
            # Try multiple date formats
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S',
                '%d %b %Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Fallback to email.utils parsing
            import email.utils
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date
            
        except Exception:
            return datetime.utcnow()
    
    def _extract_body(self, msg) -> str:
        """Extract text body from email, preferring plain text over HTML."""
        body_parts = []
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body_parts.append(self._decode_part(part))
                elif content_type == 'text/html' and not body_parts:
                    # Only use HTML if no plain text found
                    html_content = self._decode_part(part)
                    if BEAUTIFULSOUP_AVAILABLE:
                        body_parts.append(self._strip_html(html_content))
                    else:
                        body_parts.append(html_content)
        else:
            # Single part message
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                body_parts.append(self._decode_part(msg))
            elif content_type == 'text/html':
                html_content = self._decode_part(msg)
                if BEAUTIFULSOUP_AVAILABLE:
                    body_parts.append(self._strip_html(html_content))
                else:
                    body_parts.append(html_content)
        
        return '\n\n'.join(body_parts) if body_parts else 'No text content found'
    
    def _decode_part(self, part) -> str:
        """Decode email part content."""
        try:
            payload = part.get_payload(decode=True)
            if payload is None:
                return ''
            
            charset = part.get_content_charset() or 'utf-8'
            return payload.decode(charset, errors='replace')
        except Exception as e:
            print(f"Error decoding part: {e}")
            return ''
    
    def _strip_html(self, html_content: str) -> str:
        """Strip HTML tags and extract text content."""
        if not BEAUTIFULSOUP_AVAILABLE:
            return html_content
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Error stripping HTML: {e}")
            return html_content
    
    def _process_attachments(self, msg) -> List[Dict[str, Any]]:
        """Process email attachments and extract text content."""
        attachments = []
        
        if not msg.is_multipart():
            return attachments
        
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            filename = part.get_filename()
            if not filename:
                continue
            
            content_type = part.get_content_type()
            attachment_info = {
                'filename': filename,
                'content_type': content_type,
                'size': len(part.get_payload(decode=True) or b''),
                'extracted_text': ''
            }
            
            # Extract text based on content type
            if content_type == 'application/pdf':
                attachment_info['extracted_text'] = self._extract_pdf_text(part)
            elif content_type.startswith('image/'):
                attachment_info['extracted_text'] = self._extract_image_text(part)
            elif content_type in ['text/plain', 'text/html']:
                attachment_info['extracted_text'] = self._decode_part(part)
            
            attachments.append(attachment_info)
        
        return attachments
    
    def _extract_pdf_text(self, part) -> str:
        """Extract text from PDF attachment."""
        if not PYMUPDF_AVAILABLE:
            return "PDF text extraction not available (PyMuPDF not installed)"
        
        try:
            pdf_data = part.get_payload(decode=True)
            if not pdf_data:
                return ""
            
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return f"Error extracting PDF text: {str(e)}"
    
    def _extract_image_text(self, part) -> str:
        """Extract text from image using OCR."""
        if not TESSERACT_AVAILABLE:
            return "OCR not available (pytesseract not installed)"
        
        try:
            image_data = part.get_payload(decode=True)
            if not image_data:
                return ""
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting image text: {e}")
            return f"Error extracting image text: {str(e)}"
    
    def _combine_content(self, body: str, attachments: List[Dict[str, Any]]) -> str:
        """Combine email body and attachment text into full content."""
        content_parts = [body]
        
        for attachment in attachments:
            if attachment['extracted_text']:
                content_parts.append(f"\n\n--- Attachment: {attachment['filename']} ---\n")
                content_parts.append(attachment['extracted_text'])
        
        return '\n'.join(content_parts)
    
    def save_parsed_email(self, email_data: Dict[str, Any], email_id: str) -> str:
        """Save parsed email content to file."""
        try:
            # Create filename
            safe_subject = re.sub(r'[^\w\s-]', '', email_data['subject'])
            safe_subject = re.sub(r'[-\s]+', '-', safe_subject)
            filename = f"{email_id}_{safe_subject[:50]}.txt"
            filepath = settings.PARSED_EMAILS_DIR / filename
            
            # Write content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Subject: {email_data['subject']}\n")
                f.write(f"From: {email_data['sender']}\n")
                f.write(f"Date: {email_data['date'].isoformat()}\n")
                f.write(f"Label: {email_data['label']}\n")
                f.write(f"ID: {email_id}\n")
                f.write("-" * 80 + "\n\n")
                f.write(email_data['full_content'])
            
            # Also create structured notebook if open-notebook is available
            if OPEN_NOTEBOOK_AVAILABLE:
                self._create_notebook(email_data, email_id)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error saving parsed email: {e}")
            return ""
    
    def _create_notebook(self, email_data: Dict[str, Any], email_id: str) -> None:
        """Create structured notebook with simple JSON format."""
        try:
            # Create notebooks directory if it doesn't exist
            notebooks_dir = Path("notebooks")
            notebooks_dir.mkdir(exist_ok=True)
            
            # Create blocks for different content types
            blocks = []
            
            # Add email body as text block
            if email_data['body']:
                blocks.append({
                    'type': 'text',
                    'text': email_data['body'],
                    'metadata': {}
                })
            
            # Add attachment content as separate blocks
            for attachment in email_data['attachments']:
                if attachment['extracted_text']:
                    # Determine block type based on content type
                    if attachment['content_type'] == 'application/pdf':
                        block_type = 'pdf'
                    elif attachment['content_type'].startswith('image/'):
                        block_type = 'image'
                    else:
                        block_type = 'text'
                    
                    # Create block with attachment content
                    blocks.append({
                        'type': block_type,
                        'text': attachment['extracted_text'],
                        'metadata': {
                            'filename': attachment['filename'],
                            'content_type': attachment['content_type'],
                            'size': attachment['size']
                        }
                    })
            
            # Create notebook structure
            notebook_data = {
                'id': email_id,
                'title': email_data['subject'],
                'blocks': blocks,
                'metadata': {
                    'sender': email_data['sender'],
                    'date': email_data['date'].isoformat(),
                    'label': email_data['label'],
                    'has_attachments': email_data['has_attachments'],
                    'attachment_count': email_data['attachment_count'],
                    'source': 'email'
                }
            }
            
            # Save notebook to JSON file
            notebook_path = notebooks_dir / f"{email_id}.json"
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook_data, f, indent=2, default=str)
            
            print(f"✅ Created notebook: {notebook_path}")
            
        except Exception as e:
            print(f"Error creating notebook: {e}")

# Global parser instance
parser = EmailParser() 