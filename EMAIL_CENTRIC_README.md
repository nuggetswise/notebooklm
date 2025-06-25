# 📧 Email-Centric RAG Assistant

## Overview

This is an **email-first** AI assistant that allows you to chat with your emails using RAG (Retrieval-Augmented Generation). The system is designed with email as the primary source, making it easy to search, query, and get insights from your email collection.

## 🎯 Key Features

### **Email-Centric Design**
- **Email Sources**: Left panel shows all your email labels/folders with email counts
- **Chat Interface**: Main panel for asking questions about your emails
- **Persona Support**: Chat with specific personas from your emails (e.g., "Hey Nate, tell me about AI")
- **Smart Filtering**: Filter by email label, date range, and sender

### **Modern UI**
- **Clean Layout**: Two-column design with email sources on left, chat on right
- **Visual Email Cards**: See email counts and labels at a glance
- **Real-time Status**: System health and connection status
- **Responsive Design**: Works on desktop and mobile

### **AI-Powered Chat**
- **RAG Queries**: Ask questions about your emails and get AI-generated answers
- **Source Citations**: See which emails were used to generate responses
- **Contextual Responses**: AI understands the context of your email collection
- **Persona Detection**: Automatically detects when you're talking to a specific person

## 🚀 Quick Start

### 1. Start the System
```bash
# Start backend (API server)
uvicorn ingestion_api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
streamlit run app.py --server.port 8501
```

### 2. Access the Interface
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Start Chatting
1. Select an email source from the left panel (or use "All Emails")
2. Type your question in the chat interface
3. Get AI-powered answers based on your emails

## 📁 Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│ 📧 Email RAG Assistant                    ⚙️ Settings 📧 Add │
├─────────────────┬───────────────────────────────────────────┤
│ 📁 Email Sources│ 💬 Chat with Your Emails                 │
│                 │                                           │
│ 📧 AI (41)      │ 📧 Chatting with all emails              │
│ 📧 Substack (1) │                                           │
│ 📧 All Emails   │ [Chat history here...]                   │
│                 │                                           │
│ 🔍 Quick Filters│ [Ask a question about your emails...]    │
│ Days Back: 30   │                                           │
│                 │ 🚀 Send Query  🗑️ Clear Chat  📊 Sources │
│ 📊 System Status│                                           │
│ ✅ Connected    │                                           │
│ Total: 41 emails│                                           │
└─────────────────┴───────────────────────────────────────────┘
```

## 🎭 Persona Examples

The system can detect when you're talking to specific people from your emails:

- **"Hey Nate, tell me about AI"** → Nate responds in first person
- **"What did Sarah say about the project?"** → Finds Sarah's emails
- **"Summarize John's feedback"** → Extracts John's perspective

## 🔧 API Endpoints

### Core Endpoints
- `GET /status` - System status and email counts
- `GET /labels` - Available email labels
- `GET /emails` - Get emails with filtering
- `POST /query` - RAG query endpoint

### Email Management
- `POST /inbound-email` - Process new emails
- `GET /email/{id}/content` - Get specific email content
- `POST /refresh` - Refresh email index

### Persona & Prompts
- `GET /personas` - Get all personas
- `GET /prompts` - Get prompt templates
- `POST /prompts/{type}` - Update prompts

## 🛠️ Configuration

### Environment Variables
```bash
# Required
COHERE_API_KEY=your_cohere_api_key

# Optional
DATA_DIR=data
MAX_AGE_DAYS=30
```

### Email Sources
The system automatically detects email labels from your parsed emails. Common sources include:
- **AI** - AI-related newsletters and content
- **Substack** - Substack newsletters
- **Work** - Work-related emails
- **Personal** - Personal correspondence

## 🔍 Usage Examples

### Basic Queries
```
"What emails did I receive about project updates?"
"Find emails about AI from the last week"
"Summarize the latest newsletter content"
```

### Persona Queries
```
"Hey Nate, what's your take on AI safety?"
"Sarah, tell me about the meeting notes"
"John, what did you think about the proposal?"
```

### Advanced Queries
```
"Compare different perspectives on AI from my emails"
"What are the main topics in my Substack emails?"
"Find action items from recent work emails"
```

## 🎨 Customization

### Adding New Email Sources
1. Add emails to the `data/parsed_emails/` directory
2. The system will automatically detect new labels
3. Refresh the index: `POST /refresh`

### Custom Prompts
1. Access prompt templates: `GET /prompts`
2. Update prompts: `POST /prompts/{type}`
3. Test prompts: `GET /prompts/test/{type}`

## 🐛 Troubleshooting

### Common Issues
1. **Frontend not loading**: Check if Streamlit is running on port 8501
2. **API errors**: Verify backend is running on port 8000
3. **No emails found**: Check `data/parsed_emails/` directory
4. **Persona not working**: Ensure emails have proper sender information

### Debug Commands
```bash
# Check system status
curl http://localhost:8000/status

# Test RAG query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test query", "label": null}'

# Check available labels
curl http://localhost:8000/labels
```

## 🔮 Future Enhancements

- **Email Import**: Direct Gmail/Outlook integration
- **Advanced Filtering**: Date ranges, sender groups, content types
- **Email Analytics**: Insights and trends from your email collection
- **Collaborative Features**: Share email insights with team members
- **Mobile App**: Native mobile interface

---

**Built with ❤️ for email productivity** 