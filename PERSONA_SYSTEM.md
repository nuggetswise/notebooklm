# Email Persona Extraction System

## Overview

The Email Persona Extraction System automatically creates personalized profiles for email senders by extracting their first names and analyzing their communication patterns. This enhances the RAG system with contextual awareness and personalized responses.

## Features

### 🎯 **Automatic First Name Extraction**
- Extracts first names from various email sender formats:
  - Display names: `"Nate from Nate's Substack <newsletter@substack.com>"`
  - Email addresses: `"john.doe@example.com"`
  - Complex formats: `"Dr. Sarah Johnson via LinkedIn <sarah@linkedin.com>"`

### 📊 **Persona Profiles**
Each persona includes:
- **Basic Info**: First name, sender email, persona type
- **Statistics**: Email count, first/last seen dates
- **Topics**: Automatically detected from email content (AI, Tech, Business, etc.)
- **Labels**: User-defined categories
- **Context**: Rich contextual information for RAG queries

### 🧠 **Enhanced RAG Integration**
- Personalized responses based on sender context
- Topic-aware content retrieval
- Sender-specific conversation history

## How It Works

### 1. **Name Extraction Process**
```python
# Multiple extraction strategies:
1. Parse display name from email address
2. Extract from email local part (before @)
3. Pattern matching for common formats
4. Fallback to generic "Unknown" persona
```

### 2. **Topic Detection**
Automatically categorizes emails into topics:
- **AI**: artificial intelligence, machine learning, GPT, LLM
- **Tech**: technology, software, programming, startup
- **Business**: business, entrepreneur, company, investment
- **Finance**: finance, money, trading, crypto
- **Health**: health, medical, wellness, fitness
- **News**: news, update, announcement, breaking
- **Education**: education, learning, course, training
- **Marketing**: marketing, advertising, promotion, growth

### 3. **Context Generation**
Creates rich context for RAG queries:
```
"This email is from Nate (Nate from Nate's Substack <newsletter@substack.com>). 
They have sent 5 emails before. They typically write about: AI, Tech, Business, Education."
```

## API Endpoints

### Get All Personas
```http
GET /personas
```
Returns all personas with their profiles and statistics.

### Get Persona by ID
```http
GET /personas/{persona_id}
```
Returns a specific persona by its unique ID.

### Get Persona by Sender
```http
GET /personas/sender/{sender_email}
```
Returns persona information for a specific email sender.

### Get Persona Context
```http
GET /personas/context/{sender_email}
```
Returns contextual information about a sender for RAG queries.

## Usage Examples

### 1. **Basic Persona Creation**
```python
from ingestion_api.persona_extractor import persona_extractor

# Extract first name
first_name = persona_extractor.extract_first_name("Nate from Nate's Substack <newsletter@substack.com>")
# Returns: "Nate"

# Create persona
persona = persona_extractor.create_persona(
    sender="Nate from Nate's Substack <newsletter@substack.com>",
    subject="AI and Technology Update",
    content="Latest developments in artificial intelligence..."
)
```

### 2. **Enhanced RAG Queries**
```python
# Query with sender context
result = rag_pipeline.query(
    question="What did Nate say about AI?",
    label="AI",
    sender="Nate from Nate's Substack <newsletter@substack.com>"
)
```

### 3. **Persona Context for Responses**
```python
# Get contextual information
context = persona_extractor.get_persona_context("nate@example.com")
# Returns: "This email is from Nate. They have sent 3 emails before. 
# They typically write about: AI, Tech, Business."
```

## Data Storage

Personas are stored in `data/personas.json` with the following structure:

```json
{
  "nate_2288": {
    "id": "nate_2288",
    "sender": "Nate from Nate's Substack <newsletter@substack.com>",
    "first_name": "Nate",
    "display_name": "Nate from Nate's Substack <newsletter@substack.com>",
    "email_count": 5,
    "first_seen": "2025-06-25T15:44:33.790093",
    "last_seen": "2025-06-25T15:44:33.792523",
    "topics": ["AI", "Tech", "Business", "Education"],
    "labels": [],
    "persona_type": "individual"
  }
}
```

## Integration with Email Processing

The persona system is automatically integrated into the email processing pipeline:

1. **Email Ingestion**: When emails are processed, personas are automatically created/updated
2. **RAG Queries**: Persona context is included in query responses
3. **Frontend Display**: Personas can be viewed and managed through the UI

## Testing

Run the persona extraction test:
```bash
python test_persona_extraction.py
```

This will test:
- First name extraction from various formats
- Persona creation and topic detection
- Context generation
- API endpoint functionality

## Benefits

### For Users
- **Personalized Responses**: RAG system knows who sent what
- **Contextual Awareness**: Better understanding of email relationships
- **Topic Tracking**: See what topics each sender covers

### For System
- **Improved Retrieval**: Better document matching with sender context
- **Enhanced Generation**: More relevant and personalized responses
- **Relationship Mapping**: Understand communication patterns

## Future Enhancements

1. **Advanced NLP**: Use language models for better topic extraction
2. **Sentiment Analysis**: Track sender sentiment over time
3. **Communication Patterns**: Analyze email frequency and timing
4. **Relationship Mapping**: Connect related senders and topics
5. **Custom Personas**: Allow manual persona creation and editing

## Troubleshooting

### Common Issues

1. **No Personas Created**
   - Ensure emails are being processed through the pipeline
   - Check that the persona extractor is imported correctly

2. **Incorrect Name Extraction**
   - Review the name patterns in `persona_extractor.py`
   - Add custom patterns for specific formats

3. **Missing Topics**
   - Verify topic keywords are relevant to your content
   - Add custom topic categories as needed

### Debug Commands
```bash
# Check persona file
cat data/personas.json

# Test extraction
python test_persona_extraction.py

# Check API
curl http://localhost:8000/personas
```

## Configuration

Persona extraction can be customized by modifying:
- `name_patterns`: Regex patterns for name extraction
- `skip_prefixes/suffixes`: Words to ignore in email addresses
- `topics_keywords`: Topic detection keywords
- Storage location and format

The system is designed to be extensible and can be adapted to different email formats and use cases. 