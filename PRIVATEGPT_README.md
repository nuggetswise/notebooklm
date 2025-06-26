# 🔒 Private-GPT Email RAG Assistant

A **100% private** AI-powered email assistant that processes your emails locally using [Private-GPT](https://github.com/zylon-ai/private-gpt) as the backend. No data leaves your machine - everything runs locally with Ollama models and Qdrant vector storage.

---

# 👥 USER GUIDE

## 🎯 What You Can Do

Chat with your emails and documents using AI - completely privately! Ask questions about newsletters, find specific emails, get summaries, and more. Access everything through your web browser from anywhere.

## 🚀 Getting Started (For Non-Technical Users)

### 📋 Minimal Prerequisites

**You only need:**
- ✅ **A web browser** (Chrome, Firefox, Safari, or Edge)
- ✅ **An email account** (Gmail, Outlook, Yahoo, etc.)
- ✅ **Basic internet connection**
- ✅ **5 minutes of your time**

**You DON'T need:**
- ❌ Technical knowledge
- ❌ Software installation
- ❌ Programming skills
- ❌ IT support
- ❌ Special hardware

### 🎯 Your End-to-End Journey

#### **Step 1: Get Access (30 seconds)**
```
1. Open your web browser
2. Go to: https://your-email-rag-app.com
3. Click "Sign Up" or "Get Started"
4. Enter your email address
5. Create a password
6. Verify your email (check your inbox)
```

#### **Step 2: Set Up Email Forwarding (2 minutes)**

**Option A: Gmail Users**
```
1. Open Gmail in your browser
2. Click the gear icon (Settings) → "See all settings"
3. Go to "Filters and Blocked Addresses" tab
4. Click "Create a new filter"
5. In "From" field, enter: @substack.com (or your newsletter domains)
6. Click "Create filter"
7. Check "Forward it to:" and enter: your-app-email@your-domain.com
8. Click "Create filter"
```

**Option B: Outlook Users**
```
1. Open Outlook in your browser
2. Click Settings (gear icon) → "View all Outlook settings"
3. Go to "Mail" → "Rules"
4. Click "Add new rule"
5. Set condition: "From" contains "@substack.com"
6. Set action: "Forward to" your-app-email@your-domain.com
7. Click "Save"
```

**Option C: Manual Upload (No Setup Required)**
```
1. Download .eml files from your email client
2. Drag and drop them into the web app
3. That's it! No forwarding setup needed
```

#### **Step 3: Start Chatting (1 minute)**
```
1. Wait 5-10 minutes for emails to appear
2. You'll see email domains on the left (e.g., "substack.com")
3. Click on a domain to filter emails
4. Type your first question in the chat box
5. Press Enter or click "Send"
```

#### **Step 4: Explore Features (Ongoing)**
```
- Ask questions about your emails
- Upload documents (PDFs, Word docs)
- Filter by date range
- Search for specific content
- Export conversations
```

## 📧 Complete User Flow Examples

### **Scenario 1: Newsletter Management**

**Day 1: Setup**
```
Morning (5 minutes):
1. Sign up for the service
2. Set up email forwarding for newsletters
3. Wait for emails to appear

Afternoon (2 minutes):
1. Open the app
2. See "substack.com" with 15 emails
3. Ask: "What's new in AI this week?"
4. Get instant summary with citations
```

**Day 2: Daily Use**
```
Morning (1 minute):
1. Open the app
2. Ask: "Did I miss anything important yesterday?"
3. Get prioritized summary of key updates

Evening (2 minutes):
1. Ask: "Summarize the latest newsletter from Nate"
2. Get detailed breakdown of main points
3. Save important insights
```

### **Scenario 2: Document Analysis**

**Upload Documents**
```
1. Click "📧 Add Email" button
2. Choose "Upload Files" tab
3. Drag & drop your files:
   - Quarterly report.pdf
   - Budget spreadsheet.xlsx
   - Meeting notes.docx
4. Wait 30 seconds for processing
```

**Chat with Documents**
```
1. Ask: "Summarize the quarterly report"
2. Get executive summary with key metrics

3. Ask: "What are the main budget concerns?"
4. Get extracted budget information

5. Ask: "Compare Q1 vs Q2 performance"
6. Get detailed comparison analysis
```

### **Scenario 3: Information Retrieval**

**Find Specific Information**
```
1. Ask: "When did we discuss project Alpha?"
2. Get timeline of relevant emails

3. Ask: "What did John say about the deadline?"
4. Get John's specific comments with context

5. Ask: "Find emails about budget approval"
6. Get all budget-related emails with summaries
```

## 🎨 What You'll See (Visual Guide)

### **Main Dashboard Layout**
```
┌─────────────────────────────────────────────────────────┐
│ 📧 Email RAG Assistant                    ⚙️ Settings  │
├─────────────────┬───────────────────────────────────────┤
│ 📁 Email Domains│ 💬 Chat Interface                     │
│                 │                                       │
│ substack.com    │ Ask a question about your emails:     │
│ (15 emails)     │ [What's new in AI this week?]        │
│                 │                                       │
│ techcrunch.com  │ 🚀 Send Query                         │
│ (8 emails)      │                                       │
│                 │ ┌─────────────────────────────────────┐│
│ 🔍 Quick Filters│ │ AI Response:                        ││
│ Days Back: 30   │ │ Based on your emails, here are the  ││
│                 │ │ key AI updates from this week...    ││
│ 📊 System Status│ │                                     ││
│ ✅ Connected    │ │ Source: Nate's Newsletter (2 days   ││
│ 23 Total Emails │ │ ago) - "The latest developments..." ││
└─────────────────┴───────────────────────────────────────┘
```

### **Email Browser View**
```
┌─────────────────────────────────────────────────────────┐
│ 📧 Email Sources                                        │
├─────────────────────────────────────────────────────────┤
│ 👥 All Senders                                          │
│ 👤 Nate (5 emails)                                      │
│ 👤 Sarah (3 emails)                                     │
│ 👤 Mike (2 emails)                                      │
│                                                         │
│ 📅 Date Range: Last 30 days                             │
│                                                         │
│ 🔍 Search: [Find specific content...]                   │
└─────────────────────────────────────────────────────────┘
```

### **Chat Response Example**
```
User: "What emails did I receive about project updates?"

AI Response:
Based on your emails, here are the key project updates:

🚀 Project Alpha Status:
- Deadline moved to March 15th (from Sarah's email 2 days ago)
- Budget approved for additional resources
- Team meeting scheduled for next week

📊 Project Beta Progress:
- 75% completion milestone reached
- New team member joining next month
- Client feedback incorporated successfully

Source emails:
1. "Project Alpha Update" - Sarah (2 days ago)
2. "Beta Project Milestone" - Mike (1 week ago)
3. "Team Meeting Schedule" - Nate (3 days ago)

Would you like me to provide more details about any specific project?
```

## 🔧 Simple Configuration

### **Email Forwarding Made Easy**

**Gmail Step-by-Step:**
```
1. Open Gmail → Settings (gear icon)
2. Click "Filters and Blocked Addresses"
3. Click "Create a new filter"
4. In "From" field, type: @substack.com
5. Click "Create filter"
6. Check "Forward it to:"
7. Type: your-app-email@your-domain.com
8. Click "Create filter"
9. Done! ✅
```

**Outlook Step-by-Step:**
```
1. Open Outlook → Settings (gear icon)
2. Click "View all Outlook settings"
3. Go to "Mail" → "Rules"
4. Click "Add new rule"
5. Set "From" contains "@substack.com"
6. Set "Forward to" your-app-email@your-domain.com
7. Click "Save"
8. Done! ✅
```

### **File Upload Settings**
- **Supported files**: PDF, Word, Excel, PowerPoint, Text, Images
- **Max size**: 10MB per file
- **Batch upload**: Up to 10 files at once
- **Processing time**: 30-60 seconds per file

### **Privacy & Security**
- **Your data**: Stays private and secure
- **No sharing**: Never shared with third parties
- **Your control**: Export or delete anytime
- **Encryption**: All data encrypted

## 🆘 Troubleshooting (Simple Solutions)

### **Common Issues & Quick Fixes**

**"I can't see any emails"**
```
Quick Fix:
1. Check if forwarding is set up correctly
2. Wait 10-15 minutes for emails to appear
3. Try manual upload first
4. Check spam/junk folders
```

**"The app is slow"**
```
Quick Fix:
1. Refresh the page
2. Close other browser tabs
3. Check your internet connection
4. Try again in a few minutes
```

**"Upload isn't working"**
```
Quick Fix:
1. Check file size (must be under 10MB)
2. Try a different file format
3. Use Chrome or Firefox browser
4. Check file isn't corrupted
```

**"I forgot my password"**
```
Quick Fix:
1. Click "Forgot Password"
2. Enter your email address
3. Check your inbox for reset link
4. Create new password
```

### **Getting Help**
- **📧 Email Support**: support@your-domain.com
- **📞 Phone Support**: 1-800-EMAIL-RAG
- **💬 Live Chat**: Available in the app
- **📚 Help Center**: help.your-domain.com

## 🎯 Success Tips

### **Best Practices**
```
✅ Start with a few emails to test
✅ Use specific questions for better results
✅ Save important conversations
✅ Set up forwarding for all newsletters
✅ Check the app daily for updates
```

### **Question Examples**
```
Good Questions:
- "What's new in AI this week?"
- "Summarize Nate's latest newsletter"
- "Find emails about project deadlines"
- "What did I miss yesterday?"

Avoid:
- "Tell me everything" (too broad)
- "What's in my emails?" (too vague)
- "Show me all emails" (not specific)
```

### **Pro Tips**
```
💡 Use date ranges to focus on recent emails
💡 Filter by sender for specific newsletters
💡 Export important insights
💡 Use follow-up questions for more details
💡 Save frequently asked questions
```

## 🚀 Quick Start (2 Minutes)

### Step 1: Access the App
- **Open your web browser**
- **Go to**: `https://your-email-rag-app.com` (or your provided URL)
- **No installation required** - everything runs in the browser

### Step 2: Set Up Email Forwarding
```
1. In your email client (Gmail, Outlook, etc.):
   - Go to Settings → Filters/Rules
   - Create a filter for newsletters
   - Forward emails to: your-app-email@your-domain.com
2. Or use the manual upload feature
```

### Step 3: Start Chatting
- **Upload emails** using the file uploader
- **Ask questions** in the chat interface
- **Get instant AI responses** about your emails

## 📧 End-to-End User Flow

### Scenario 1: Chat with Your Emails

**Step 1: Email Setup**
```
Option A - Automatic Forwarding:
1. Set up email forwarding in your email client
2. Emails automatically appear in the app

Option B - Manual Upload:
1. Download .eml files from your email client
2. Upload them through the web interface
3. Process and start chatting
```

**Step 2: Start Chatting**
```
1. Open the web app in your browser
2. See your email domains on the left (e.g., "substack.com")
3. Click on a domain to filter emails
4. Type your question in the chat box
```

**Step 3: Ask Questions**
```
Examples:
- "What emails did I receive about AI this week?"
- "Summarize the latest newsletter from Nate"
- "Find emails about project updates"
- "What did I miss in my newsletters yesterday?"
```

**Step 4: Get AI Responses**
```
The AI will:
- Search through your emails
- Find relevant content
- Generate a helpful response
- Show you the source emails
```

### Scenario 2: Upload & Chat with Documents

**Step 1: Upload Documents**
```
1. Click "📧 Add Email" button
2. Choose "Upload Files" tab
3. Drag & drop or select files:
   - PDF reports
   - Word documents
   - Text files
   - Images (with text)
4. Click "Upload & Process"
```

**Step 2: Chat with Documents**
```
1. Ask questions about your documents:
   - "Summarize this report"
   - "What are the key findings?"
   - "Find information about budgets"
   - "Compare different sections"
```

**Step 3: Get Insights**
```
The AI will:
- Process your documents
- Extract key information
- Answer your questions
- Show relevant sections
```

### Scenario 3: Advanced Email Management

**Step 1: Filter & Search**
```
1. Use date range slider (1-365 days)
2. Filter by sender domain
3. Filter by specific senders
4. Search across all content
```

**Step 2: Get Analytics**
```
1. Click "📊 Show Sources" to see:
   - Email count by domain
   - Sender statistics
   - Date distribution
   - Content summaries
```

**Step 3: Export & Share**
```
1. Copy chat responses
2. Export email lists
3. Share insights with team
```

## 🎯 Common Use Cases

### 📰 Newsletter Management
```
Q: "What's new in AI this week?"
A: [AI summarizes latest AI newsletters with citations]

Q: "Did I miss any important updates?"
A: [AI checks recent emails and highlights key points]
```

### 📊 Document Analysis
```
Q: "Summarize this quarterly report"
A: [AI provides executive summary with key metrics]

Q: "Find budget information"
A: [AI extracts and explains budget details]
```

### 🔍 Information Retrieval
```
Q: "When did we discuss project X?"
A: [AI finds relevant emails with dates and context]

Q: "What did John say about the deadline?"
A: [AI searches for John's emails about deadlines]
```

## 🎨 User Interface Guide

### Main Dashboard
- **Left Panel**: Email domains and filters
- **Right Panel**: Chat interface
- **Top Bar**: System status and controls

### Chat Features
- **Real-time responses**: Get answers instantly
- **Source citations**: See which emails were used
- **Follow-up questions**: Ask for more details
- **Export options**: Save conversations

### Email Browser
- **Domain view**: See all sender domains
- **Sender view**: Filter by specific people
- **Date range**: Focus on recent emails
- **Search**: Find specific content

## 🔧 User Configuration

### Email Forwarding Setup

**Gmail:**
1. Go to Settings → Filters and Blocked Addresses
2. Create new filter for newsletters
3. Add forwarding address: `your-app-email@your-domain.com`

**Outlook:**
1. Go to Rules → Create new rule
2. Set conditions for newsletters
3. Add forwarding action

**Apple Mail:**
1. Go to Mail → Preferences → Rules
2. Create new rule for newsletters
3. Set action to forward to your app email

### File Upload Settings
- **Supported formats**: PDF, DOCX, TXT, PNG, JPG
- **Max file size**: 10MB per file
- **Batch upload**: Up to 10 files at once

### Privacy Settings
- **Secure processing**: All data processed securely
- **Encrypted storage**: Data encrypted at rest
- **Access control**: Only you can access your data

## 🆘 Troubleshooting

### Common Issues

**Can't access the app:**
```
1. Check your internet connection
2. Verify the URL is correct
3. Try refreshing the page
4. Contact support if issues persist
```

**No emails showing:**
```
1. Verify email forwarding is set up correctly
2. Check your email client's forwarding settings
3. Try manual upload first
4. Check spam/junk folders
```

**Slow responses:**
```
1. Check your internet connection
2. Try refreshing the page
3. Close other browser tabs
4. Contact support if consistently slow
```

**Upload fails:**
```
1. Check file format is supported
2. Ensure file size < 10MB
3. Try smaller files first
4. Check browser compatibility
```

### Browser Compatibility
- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

### Getting Help
- **Documentation**: Check this README
- **Support**: Contact your system administrator
- **Email**: support@your-domain.com
- **Phone**: [Your support number]

## 🔐 Security & Privacy

### Data Protection
- **End-to-end encryption**: All data encrypted in transit
- **Secure storage**: Data stored in secure cloud infrastructure
- **Access control**: Multi-factor authentication available
- **Audit logs**: All access is logged and monitored

### Privacy Features
- **No data sharing**: Your data is never shared with third parties
- **Local processing**: AI processing happens on secure servers
- **Data retention**: Configurable data retention policies
- **Export/delete**: Full control over your data

## 📱 Mobile Access

### Mobile Browser
- **Responsive design**: Works on all mobile browsers
- **Touch-friendly**: Optimized for touch interfaces
- **Offline capability**: Basic features work offline

### Mobile App (Future)
- **Native iOS/Android apps** planned
- **Push notifications** for new emails
- **Offline sync** capabilities

## 🔄 Data Management

### Backup & Export
```
1. Export all your emails: Settings → Export Data
2. Download chat history: Chat → Export Conversation
3. Backup settings: Settings → Backup Configuration
```

### Data Cleanup
```
1. Delete old emails: Email Browser → Select → Delete
2. Clear chat history: Chat → Clear History
3. Remove documents: File Manager → Select → Delete
```

### Account Management
```
1. Update profile: Settings → Profile
2. Change password: Settings → Security
3. Manage devices: Settings → Devices
4. Deactivate account: Settings → Account → Deactivate
```

## 📱 Offline Capabilities

### 🔌 What Works Offline

**Full offline functionality is available since Private-GPT runs locally:**

#### **✅ Available Offline**
```
🤖 Core AI Features
- AI chat and question answering (100% local)
- Email analysis and summarization
- Document processing and insights
- Semantic search across emails
- Context-aware responses
- All Private-GPT functionality

📱 Basic Features
- View previously loaded emails and documents
- Read cached chat conversations
- Access saved responses and insights
- Use advanced search on all content
- View email metadata and summaries
- Access privacy settings and preferences

📱 Mobile App (Future)
- Full AI chat functionality
- Offline email analysis
- Local document processing
- Advanced search capabilities
- Draft message composition
- Settings management
- Data export (previously downloaded)
```

#### **❌ Requires Internet Connection**
```
🌐 Synchronization Only
- New email ingestion and forwarding
- Document upload (initial processing)
- Real-time email notifications
- System updates and improvements
- User authentication (initial)
- Subscription management
- Data backup and sync
```

### 🏗️ Offline Architecture

#### **How Offline Works**
```
🤖 Local AI Processing
- Private-GPT runs completely locally
- Ollama models process on your device
- Qdrant vector database local storage
- No internet required for AI features
- Full privacy and security offline

📱 Local Storage
- Browser cache for recent emails
- IndexedDB for offline data
- Service Worker for offline access
- Local storage for preferences
- Local vector embeddings

📱 Sync Strategy
- Background sync when online (for new emails)
- Conflict resolution for changes
- Incremental data updates
- Offline-first AI processing
```

#### **Data Caching Strategy**
```
💾 Cache Management
- All emails and documents (local storage)
- Vector embeddings (Qdrant local)
- AI models (Ollama local)
- Chat conversation history
- User preferences and settings
- Search indexes for all content

💾 Cache Limits
- Limited only by device storage
- Automatic cleanup of old data
- Priority-based caching
- User-controlled cache management
- Local model optimization
```

### 📱 Mobile Offline Experience

#### **Mobile App Offline Features**
```
📱 Full Offline Capabilities
- Complete AI chat functionality
- Email analysis and processing
- Document analysis and insights
- Advanced search across all content
- Draft message composition
- Settings management
- Export all data locally

📱 Sync Behavior
- Background sync for new emails only
- Manual sync options
- Conflict resolution
- Progress indicators
- Error handling and retry
- Local AI processing priority
```

#### **Offline Advantages**
```
✅ Offline Benefits
- Full AI functionality without internet
- Faster processing (no network latency)
- Complete privacy (no data transmission)
- No dependency on external services
- Works in any environment
- Reduced battery usage (no network calls)
```

### 🔄 Online/Offline Transition

#### **Going Offline**
```
📱 Seamless Transition
- No interruption to AI features
- All functionality remains available
- Local processing continues
- No degradation of capabilities
- Clear offline status indicator
- Sync status for new emails only

📱 User Experience
- Uninterrupted AI chat
- Full document processing
- Complete search functionality
- All Private-GPT features work
- Sync status for email updates
```

#### **Coming Back Online**
```
🌐 Reconnection Process
- Sync new emails automatically
- Background data synchronization
- Conflict resolution
- User notification of sync completion
- No interruption to AI features

🌐 Sync Priority
- New email ingestion first
- Document uploads
- Background processing
- System updates
- Performance optimization
```

### 🎯 Offline Use Cases

#### **Common Offline Scenarios**
```
✈️ Travel & Commuting
- Full AI chat on flights
- Complete email analysis offline
- Document processing anywhere
- Advanced search functionality
- All insights and summaries

🏢 Limited Connectivity
- Rural areas with poor internet
- Office buildings with restrictions
- Conference venues with limited WiFi
- International travel with data limits
- Emergency situations
- Secure environments (no internet allowed)
```

#### **Offline Workflows**
```
📋 Complete Offline Workflow
1. Process emails and documents when online
2. Go offline with full AI capabilities
3. Chat with AI about your emails
4. Analyze documents and get insights
5. Search and find information
6. Generate summaries and reports
7. Reconnect only for new data sync

📋 Reconnection Workflow
1. Sync new emails when back online
2. Process new documents
3. Update local indexes
4. Continue with full functionality
5. No interruption to AI features
```

### ⚙️ Offline Configuration

#### **User Settings**
```
🎛️ Offline Preferences
- Enable/disable offline mode
- Set local storage limits
- Choose sync frequency for new emails
- Select offline content priority
- Configure auto-sync behavior
- Manage local AI model settings

🎛️ Storage Management
- View local storage usage
- Manage local models
- Clear cached data
- Manage download queue
- Set retention policies
- Export all data locally
```

#### **System Settings**
```
⚙️ Local Configuration
- Maximum local storage: Device dependent
- Model retention: All local models
- Sync frequency: Every 15 minutes (new emails only)
- Background sync: Enabled for new data
- AI processing: 100% local
- Conflict resolution: Local wins for AI features
```

### 📊 Offline Performance

#### **Performance Characteristics**
```
⚡ Offline Performance
- Instant AI responses (no network latency)
- Faster processing (local computation)
- Immediate search results
- Responsive document analysis
- No bandwidth limitations
- Reduced battery usage

⚡ AI Performance
- Full Private-GPT capabilities
- Local Ollama model processing
- Qdrant vector search
- Complete email analysis
- Advanced document processing
- Real-time chat responses
```

#### **Storage Requirements**
```
💾 Storage Needs
- Email storage: ~1MB per 100 emails
- Document storage: ~5MB per document
- Chat history: ~1MB per 1000 messages
- Vector embeddings: ~10MB per 1000 emails
- AI models: ~4-8GB (Ollama models)
- Total recommended: 10GB+ free space
```

### 🔧 Technical Implementation

#### **Offline Technologies**
```
🛠️ Implementation
- Private-GPT for local AI processing
- Ollama for local model inference
- Qdrant for local vector storage
- Service Workers for offline access
- IndexedDB for local data storage
- Web App Manifest for mobile

🛠️ AI Processing
- Local model inference
- Local vector search
- Local document processing
- Local email analysis
- Local chat generation
- No external API calls
```

#### **Browser Support**
```
🌐 Browser Compatibility
- Chrome: Full offline AI support
- Firefox: Full offline AI support
- Safari: Limited offline AI support
- Edge: Full offline AI support
- Mobile browsers: Varies by platform
```

### 🎯 Offline Best Practices

#### **For Users**
```
✅ Best Practices
- Sync emails and documents when online
- Keep local models updated
- Monitor local storage usage
- Use offline mode for AI-intensive tasks
- Reconnect regularly for new data sync
- Leverage full AI capabilities offline

❌ Avoid
- Expecting new email processing offline
- Ignoring local storage limits
- Forgetting to sync new documents
- Using outdated local models
- Ignoring sync conflicts for new data
```

#### **For Developers**
```
🔧 Development Guidelines
- Implement offline-first AI processing
- Provide clear offline AI indicators
- Handle local model management
- Optimize for local storage efficiency
- Test offline AI scenarios thoroughly

🔧 User Experience
- Clear communication about offline AI capabilities
- Intuitive local model controls
- Progress indicators for local processing
- Error handling for local operations
- Seamless online/offline AI transitions
```

### 📱 Future Offline Enhancements

#### **Planned Features**
```
🚀 Upcoming Improvements
- Enhanced local AI model performance
- Offline collaborative features
- Local model optimization
- Better local search capabilities
- Offline model training capabilities

🚀 Mobile Enhancements
- Native offline AI processing
- Local background processing
- Offline model updates
- Offline-first design
- Cross-device local sync
```

#### **Advanced Offline Capabilities**
```
🔮 Future Possibilities
- Local model fine-tuning
- Offline email composition with AI
- Advanced offline document editing
- Local model sharing
- Peer-to-peer AI processing
```

### 📞 Offline Support

#### **Getting Help with Offline Issues**
```
📧 Offline Support
- Email: offline-support@your-domain.com
- Documentation: offline.your-domain.com
- FAQ: Common offline AI questions
- Troubleshooting guide: Step-by-step solutions

📧 Offline Resources
- Offline AI user guide
- Local model management
- Storage optimization tips
- Performance optimization
- Best practices guide
```

**Note**: Since this is Private-GPT, all AI chat and analysis features work completely offline. You only need internet for syncing new emails and documents. The core AI functionality is 100% local and private.

---

# 👨‍💻 DEVELOPER GUIDE

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Load Balancer   │    │   Email Source  │
│   (Any Device)  │◄──►│  (Cloudflare)    │◄──►│   User Emails   │
│                 │    │                  │    │                 │
│ • React/Vue UI  │    │ • SSL/TLS        │    │ • Gmail/Outlook │
│ • Mobile App    │    │ • CDN            │    │ • Auto-forward  │
│ • PWA Support   │    │ • Rate Limiting  │    │ • Manual Upload │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Application     │
                       │  Layer           │
                       │                  │
                       │ • Streamlit API  │
                       │ • Private-GPT    │
                       │ • Email Parser   │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Infrastructure  │
                       │  Layer           │
                       │                  │
                       │ • Kubernetes     │
                       │ • Qdrant Cloud   │
                       │ • Ollama Cloud   │
                       │ • Redis Cache    │
                       └──────────────────┘
```

## 🚀 Development Setup

### Prerequisites

- **Docker & Docker Compose** (for local development)
- **Python 3.8+** (for backend development)
- **Node.js 18+** (for frontend development)
- **PostgreSQL** (for production database)
- **Redis** (for caching and sessions)

### 1. Local Development Environment

```bash
# Clone the repository
git clone <repository>
cd emailragnew

# Backend setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev

# Start development services
docker-compose -f docker-compose.dev.yml up -d
```

### 2. Production Environment Setup

```bash
# Deploy to cloud infrastructure
# Option 1: Kubernetes
kubectl apply -f k8s/

# Option 2: Docker Swarm
docker stack deploy -c docker-compose.prod.yml email-rag

# Option 3: AWS ECS
aws ecs create-service --cluster email-rag --service-definition email-rag-service
```

### 3. Multi-Tenant Configuration

```python
# Tenant management service
class TenantService:
    def __init__(self):
        self.db = Database()
    
    def create_tenant(self, name: str, domain: str, subscription_tier: str = "free"):
        tenant = {
            "id": str(uuid.uuid4()),
            "name": name,
            "domain": domain,
            "subscription_tier": subscription_tier,
            "settings": self.get_default_settings(subscription_tier),
            "created_at": datetime.utcnow()
        }
        return self.db.create_tenant(tenant)
    
    def get_tenant_limits(self, tenant_id: str):
        tenant = self.db.get_tenant(tenant_id)
        limits = {
            "free": {"emails": 1000, "storage_gb": 1, "api_calls": 100},
            "pro": {"emails": 10000, "storage_gb": 10, "api_calls": 1000},
            "enterprise": {"emails": 100000, "storage_gb": 100, "api_calls": 10000}
        }
        return limits.get(tenant["subscription_tier"], limits["free"])
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Production environment
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/email_rag
REDIS_URL=redis://redis:6379
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434

# Security
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-encryption-key
API_KEY_SECRET=your-api-key-secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Cloud Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=email-rag-storage
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
METRICS_ENABLED=true

# Multi-tenancy
TENANT_ISOLATION=true
DEFAULT_SUBSCRIPTION_TIER=free
MAX_TENANTS_PER_INSTANCE=1000
```

### Database Schema (Multi-tenant)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- User-Tenant mapping
CREATE TABLE user_tenants (
    user_id UUID REFERENCES users(id),
    tenant_id UUID REFERENCES tenants(id),
    role VARCHAR(50) DEFAULT 'user',
    PRIMARY KEY (user_id, tenant_id)
);

-- Emails table (partitioned by tenant)
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    subject VARCHAR(500),
    sender VARCHAR(255),
    recipient VARCHAR(255),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
) PARTITION BY HASH (tenant_id);

-- Create partitions for each tenant
CREATE TABLE emails_tenant_1 PARTITION OF emails
    FOR VALUES WITH (modulus 10, remainder 0);
```

### API Rate Limiting

```python
# Rate limiting configuration
from fastapi import FastAPI, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute per user
async def chat_with_emails(request: Request, user: User = Depends(get_current_user)):
    # Chat implementation
    pass

@app.post("/api/upload")
@limiter.limit("5/minute")  # 5 uploads per minute per user
async def upload_email(request: Request, user: User = Depends(get_current_user)):
    # Upload implementation
    pass
```

## 🔒 Security Implementation

### Authentication & Authorization

```python
# JWT Authentication
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

class UserAuth:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = "HS256"
        self.access_token_expires = timedelta(hours=1)
    
    def create_access_token(self, user_id: str, tenant_id: str):
        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "exp": datetime.utcnow() + self.access_token_expires
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Multi-factor authentication
class MFAService:
    def generate_totp(self, user_id: str) -> str:
        # Generate TOTP secret
        secret = pyotp.random_base32()
        # Store in database
        return secret
    
    def verify_totp(self, user_id: str, token: str) -> bool:
        # Verify TOTP token
        secret = self.get_user_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
```

### Data Encryption

```python
# Encryption service
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        self.cipher = Fernet(self.key)
    
    def encrypt_email_content(self, content: str) -> str:
        encrypted = self.cipher.encrypt(content.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_email_content(self, encrypted_content: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_content)
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
```

## 📊 Monitoring & Observability

### Application Monitoring

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
EMAIL_PROCESSING_TIME = Histogram('email_processing_duration_seconds', 'Email processing time')

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

### Logging Configuration

```python
# Structured logging
import structlog
import logging

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info("email_processed", 
    user_id=user.id, 
    tenant_id=tenant.id, 
    email_count=len(emails),
    processing_time=duration
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest --cov=./ --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t email-rag-frontend:${{ github.sha }} ./frontend
          docker build -t email-rag-backend:${{ github.sha }} ./backend
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push email-rag-frontend:${{ github.sha }}
          docker push email-rag-backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/email-rag-frontend frontend=email-rag-frontend:${{ github.sha }}
          kubectl set image deployment/email-rag-backend backend=email-rag-backend:${{ github.sha }}
```

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_email_processing.py
import pytest
from unittest.mock import Mock, patch
from email_rag.services.email_processor import EmailProcessor

class TestEmailProcessor:
    @pytest.fixture
    def email_processor(self):
        return EmailProcessor()
    
    @pytest.fixture
    def sample_email(self):
        return {
            "subject": "Test Email",
            "sender": "test@example.com",
            "content": "This is a test email content"
        }
    
    def test_process_email(self, email_processor, sample_email):
        result = email_processor.process(sample_email)
        assert result["subject"] == "Test Email"
        assert result["processed"] == True
    
    @patch('email_rag.services.email_processor.PrivateGPTClient')
    def test_ingest_to_privategpt(self, mock_client, email_processor, sample_email):
        mock_client.return_value.ingest.return_value = {"status": "success"}
        result = email_processor.ingest_to_privategpt(sample_email)
        assert result["status"] == "success"
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from email_rag.main import app

client = TestClient(app)

class TestEmailRAGIntegration:
    def test_chat_endpoint(self):
        response = client.post("/api/chat", json={
            "message": "What emails did I receive about AI?",
            "user_id": "test-user"
        })
        assert response.status_code == 200
        assert "answer" in response.json()
    
    def test_upload_endpoint(self):
        with open("tests/fixtures/test_email.eml", "rb") as f:
            response = client.post("/api/upload", files={"file": f})
        assert response.status_code == 200
        assert "email_id" in response.json()
```

### Load Testing

```python
# tests/load_test.py
import asyncio
import aiohttp
import time

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):  # 100 concurrent users
            task = asyncio.create_task(send_chat_request(session, i))
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Processed {len(results)} requests in {end_time - start_time:.2f} seconds")

async def send_chat_request(session, user_id):
    async with session.post("http://localhost:8001/api/chat", json={
        "message": f"Test message from user {user_id}",
        "user_id": f"user-{user_id}"
    }) as response:
        return await response.json()
```

## 📈 Performance Optimization

### Caching Strategy

```python
# Redis caching
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(expire_time=1800)  # 30 minutes
def get_email_summary(user_id: str, date_range: str):
    # Expensive email summary generation
    pass
```

### Database Optimization

```sql
-- Indexes for performance
CREATE INDEX idx_emails_tenant_date ON emails(tenant_id, created_at);
CREATE INDEX idx_emails_sender ON emails(sender);
CREATE INDEX idx_emails_subject ON emails USING gin(to_tsvector('english', subject));

-- Partitioning for large datasets
CREATE TABLE emails_2024_01 PARTITION OF emails
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for analytics
CREATE MATERIALIZED VIEW email_stats AS
SELECT 
    tenant_id,
    DATE(created_at) as date,
    COUNT(*) as email_count,
    COUNT(DISTINCT sender) as unique_senders
FROM emails
GROUP BY tenant_id, DATE(created_at);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW email_stats;
```

## 🔄 Migration from Current System

### Data Migration Script

```python
# scripts/migrate_to_production.py
import asyncio
import aiohttp
from email_rag.database import Database
from email_rag.services.email_processor import EmailProcessor

async def migrate_emails():
    db = Database()
    processor = EmailProcessor()
    
    # Get all emails from current system
    emails = db.get_all_emails()
    
    # Process in batches
    batch_size = 100
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        
        # Process each email
        for email in batch:
            # Convert to new format
            processed_email = processor.convert_format(email)
            
            # Ingest to Private-GPT
            await processor.ingest_to_privategpt(processed_email)
            
            # Update database
            db.update_email_status(email.id, "migrated")
        
        print(f"Migrated batch {i//batch_size + 1}")

if __name__ == "__main__":
    asyncio.run(migrate_emails())
```

### Blue-Green Deployment

```yaml
# kubernetes/blue-green-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: email-rag-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: email-rag
      version: blue
  template:
    metadata:
      labels:
        app: email-rag
        version: blue
    spec:
      containers:
      - name: email-rag
        image: email-rag:blue
        ports:
        - containerPort: 8001

---
apiVersion: v1
kind: Service
metadata:
  name: email-rag-service
spec:
  selector:
    app: email-rag
    version: blue  # Switch to green for new deployment
  ports:
  - port: 80
    targetPort: 8001
```

## 🔒 Security & Compliance

### GDPR Compliance

```python
# Data privacy service
class PrivacyService:
    def __init__(self):
        self.db = Database()
    
    def export_user_data(self, user_id: str) -> dict:
        """Export all user data for GDPR compliance"""
        user_data = {
            "profile": self.db.get_user_profile(user_id),
            "emails": self.db.get_user_emails(user_id),
            "chat_history": self.db.get_chat_history(user_id),
            "settings": self.db.get_user_settings(user_id)
        }
        return user_data
    
    def delete_user_data(self, user_id: str):
        """Delete all user data (right to be forgotten)"""
        # Anonymize emails
        self.db.anonymize_user_emails(user_id)
        
        # Delete chat history
        self.db.delete_chat_history(user_id)
        
        # Delete user profile
        self.db.delete_user(user_id)
        
        # Notify Private-GPT to delete embeddings
        self.delete_embeddings(user_id)
    
    def anonymize_user_emails(self, user_id: str):
        """Anonymize email content while preserving structure"""
        emails = self.db.get_user_emails(user_id)
        for email in emails:
            email.content = self.anonymize_text(email.content)
            email.sender = "REDACTED"
            self.db.update_email(email)
```

### Audit Logging

```python
# Audit service
class AuditService:
    def __init__(self):
        self.db = Database()
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: dict):
        """Log all user actions for audit purposes"""
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details,
            "timestamp": datetime.utcnow(),
            "ip_address": self.get_client_ip(),
            "user_agent": self.get_user_agent()
        }
        self.db.insert_audit_log(audit_entry)
    
    def get_audit_trail(self, user_id: str, start_date: datetime, end_date: datetime):
        """Get audit trail for compliance reporting"""
        return self.db.get_audit_logs(user_id, start_date, end_date)
```

## 💰 Subscription Management

### Billing Integration

```python
# Stripe integration for billing
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    def __init__(self):
        self.stripe = stripe
    
    def create_subscription(self, user_id: str, plan: str):
        """Create a new subscription"""
        customer = self.stripe.Customer.create(
            email=user.email,
            metadata={"user_id": user_id}
        )
        
        subscription = self.stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": self.get_price_id(plan)}],
            metadata={"user_id": user_id}
        )
        
        return subscription
    
    def get_usage_limits(self, user_id: str):
        """Get current usage and limits"""
        user = self.db.get_user(user_id)
        subscription = self.stripe.Subscription.retrieve(user.stripe_subscription_id)
        
        limits = {
            "free": {"emails": 1000, "storage_gb": 1, "api_calls": 100},
            "pro": {"emails": 10000, "storage_gb": 10, "api_calls": 1000},
            "enterprise": {"emails": 100000, "storage_gb": 100, "api_calls": 10000}
        }
        
        return limits.get(subscription.plan, limits["free"])
```

## 📚 Additional Resources

- [Private-GPT Documentation](https://docs.privategpt.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [ChatWise Features](https://chatwise.app/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 🤝 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: [Project Wiki](link-to-wiki)
- **Enterprise Support**: enterprise@your-domain.com

---

**Built with ❤️ for privacy-first AI email processing**

## 🔐 Data Privacy & Security

### 🛡️ How We Protect Your Data

**Your privacy is our top priority.** Here's exactly how we ensure your emails and documents remain completely private and secure:

### 🔒 Data Privacy Guarantees

#### **100% Private Processing**
```
✅ Your emails are processed in isolated environments
✅ Each user's data is completely separated
✅ No cross-user data access or sharing
✅ AI models only see your data, never others'
```

#### **Zero Data Sharing**
```
✅ We never sell your data to third parties
✅ We never share your emails with advertisers
✅ We never use your data for training other AI models
✅ We never access your data for any purpose other than serving you
```

#### **Complete Data Control**
```
✅ You own all your data
✅ Export your data anytime
✅ Delete your data completely
✅ Control what gets processed
```

### 🏗️ Technical Security Measures

#### **Data Encryption**
```
🔐 End-to-End Encryption
- All data encrypted in transit (HTTPS/TLS 1.3)
- All data encrypted at rest (AES-256)
- Database encryption with customer-managed keys
- File-level encryption for all uploads

🔐 Encryption Keys
- Unique encryption keys per user
- Keys never stored with data
- Hardware Security Modules (HSM) for key management
- Automatic key rotation every 90 days
```

#### **Infrastructure Security**
```
🛡️ Cloud Security
- SOC 2 Type II certified infrastructure
- ISO 27001 compliant data centers
- Regular security audits and penetration testing
- 24/7 security monitoring and threat detection

🛡️ Network Security
- Private network isolation
- Firewall protection at multiple layers
- DDoS protection and mitigation
- Intrusion detection and prevention systems
```

#### **Application Security**
```
🔒 Code Security
- Regular security code reviews
- Automated vulnerability scanning
- Dependency vulnerability monitoring
- Secure development lifecycle (SDL)

🔒 Access Control
- Multi-factor authentication (MFA) required
- Role-based access control (RBAC)
- Session management and timeout
- Audit logging for all access
```

### 📊 Data Flow & Processing

#### **How Your Data Moves**
```
1. Email Forwarding → Encrypted HTTPS → Secure Server
2. Secure Server → Isolated Processing → Private-GPT
3. Private-GPT → Local Processing → Encrypted Storage
4. Encrypted Storage → Secure Retrieval → Your Browser
```

#### **Data Processing Isolation**
```
👤 User Isolation
- Separate database schemas per user
- Isolated Private-GPT instances
- Dedicated vector storage collections
- No data leakage between users

🔒 Processing Isolation
- Containerized processing environments
- Memory isolation between users
- Temporary data cleanup after processing
- No persistent cross-user data storage
```

### 🏢 Compliance & Certifications

#### **Regulatory Compliance**
```
📋 GDPR Compliance
- Right to be forgotten (data deletion)
- Data portability (export functionality)
- Consent management
- Privacy by design implementation

📋 SOC 2 Type II
- Security, availability, and confidentiality
- Annual third-party audits
- Continuous monitoring and reporting
- Incident response procedures

📋 ISO 27001
- Information security management
- Risk assessment and treatment
- Security controls and procedures
- Regular compliance audits
```

#### **Industry Standards**
```
🏆 Security Standards
- OWASP Top 10 compliance
- NIST Cybersecurity Framework
- Cloud Security Alliance (CSA) STAR
- Regular penetration testing

🏆 Privacy Standards
- Privacy Shield compliance (if applicable)
- CCPA compliance for California users
- PIPEDA compliance for Canadian users
- Local privacy law adherence
```

### 🔍 Transparency & Control

#### **What We Can See**
```
👁️ Limited Access
- Email metadata (sender, subject, date)
- Processing logs (for debugging only)
- Usage statistics (anonymized)
- System performance metrics

👁️ What We Cannot See
- Email content (encrypted)
- Document content (encrypted)
- Chat conversations (encrypted)
- Personal information (encrypted)
```

#### **Your Control Options**
```
🎛️ Data Control
- Pause processing anytime
- Delete specific emails or documents
- Export all your data
- Complete account deletion

🎛️ Privacy Settings
- Control what gets processed
- Set data retention periods
- Manage sharing permissions
- Configure notification preferences
```

### 🚨 Incident Response

#### **Security Incident Handling**
```
🚨 Response Plan
- 24/7 security monitoring
- Immediate incident detection
- Automated threat response
- Human security team escalation

🚨 Communication
- Transparent incident reporting
- User notification within 24 hours
- Regular status updates
- Post-incident analysis and lessons learned
```

#### **Data Breach Protection**
```
🛡️ Breach Prevention
- Regular security assessments
- Employee security training
- Vendor security reviews
- Continuous vulnerability management

🛡️ Breach Response
- Immediate containment procedures
- Forensic analysis and investigation
- Regulatory notification compliance
- User support and assistance
```

### 🔐 Privacy by Design

#### **Built-in Privacy Features**
```
🏗️ Architecture
- Privacy-first design principles
- Data minimization (only collect what's needed)
- Purpose limitation (clear use cases only)
- Storage limitation (automatic data cleanup)

🏗️ Implementation
- Default privacy settings
- Granular consent management
- Transparent data practices
- User-friendly privacy controls
```

#### **Ongoing Privacy Improvements**
```
📈 Continuous Enhancement
- Regular privacy impact assessments
- User feedback integration
- Industry best practice adoption
- Regulatory requirement updates

📈 Privacy Innovation
- Advanced encryption techniques
- Zero-knowledge proof systems
- Federated learning approaches
- Privacy-preserving AI methods
```

### 📞 Privacy Support

#### **Getting Privacy Help**
```
📧 Privacy Questions
- Email: privacy@your-domain.com
- Phone: 1-800-PRIVACY
- Live chat: Available in app
- FAQ: privacy.your-domain.com

📧 Data Requests
- Data export: export@your-domain.com
- Data deletion: delete@your-domain.com
- Privacy policy: privacy.your-domain.com
- Legal inquiries: legal@your-domain.com
```

#### **Privacy Resources**
```
📚 Documentation
- Privacy Policy: Detailed data practices
- Terms of Service: Usage rights and responsibilities
- Data Processing Agreement: GDPR compliance
- Security Whitepaper: Technical security details

📚 Tools
- Privacy Dashboard: Manage your data
- Data Export Tool: Download your information
- Consent Manager: Control data processing
- Privacy Settings: Configure preferences
```

### 🎯 Privacy Commitments

#### **Our Promises to You**
```
🤝 Privacy Commitments
- We will never sell your data
- We will never share your emails
- We will always encrypt your data
- We will always give you control
- We will always be transparent
- We will always protect your privacy

🤝 Security Commitments
- We will always use best-in-class security
- We will always monitor for threats
- We will always respond to incidents
- We will always maintain compliance
- We will always audit our systems
- We will always train our team
```

#### **Your Privacy Rights**
```
⚖️ Your Rights
- Right to access your data
- Right to correct your data
- Right to delete your data
- Right to export your data
- Right to restrict processing
- Right to data portability
- Right to object to processing
- Right to withdraw consent
```

This comprehensive privacy and security framework ensures that your data remains completely private and secure while using our email RAG assistant. We believe privacy is a fundamental right, not a feature.

---

## 🔧 **Technical Implementation Guide**

### **📊 Current vs. Planned Tech Stack Analysis**

#### **🔄 Current Architecture (Cloud-Dependent)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gmail API     │───▶│  Email Parser   │───▶│  Vector Store   │
│   (Substack)    │    │  (Content +     │    │   (FAISS)       │
│                 │    │   Metadata)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │◀───│   RAG Pipeline  │◀───│   Cohere API    │
│  (Streamlit)    │    │  (Query +       │    │ (Embed + Gen)   │
│                 │    │   Response)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Gemini API    │
                       │   (Fallback)    │
                       └─────────────────┘
```

#### **🎯 Planned Architecture (100% Local)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Email Source  │───▶│  Email Parser   │───▶│  Private-GPT    │
│   (Local Files) │    │  (Content +     │    │   (Ingestion)   │
│                 │    │   Metadata)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │◀───│  Private-GPT    │◀───│   Qdrant DB     │
│  (Streamlit)    │    │  (Query API)    │    │ (Local Vector)  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (Local LLM)   │
                       └─────────────────┘
```

### **🔄 Technology Delta Analysis**

#### **❌ Components to Remove**
```python
# Current Cloud Dependencies
- cohere>=4.0.0,<5.0.0          # Cloud embeddings & generation
- google-generativeai>=0.3.0    # Cloud Gemini API
- openai>=1.86.0,<2.0.0        # Cloud OpenAI API
- faiss-cpu>=1.7.4,<2.0.0      # Local FAISS (replaced by Qdrant)
- sentence-transformers>=2.2.0  # Cloud embedding models
```

#### **✅ Components to Add**
```python
# New Local Dependencies
- private-gpt-client>=0.1.0     # Private-GPT API client
- qdrant-client>=1.7.0          # Qdrant vector database
- ollama>=0.1.0                 # Ollama client for local LLMs
- docker-compose>=1.29.0        # Container orchestration
- pydantic>=2.5.0               # Data validation (already present)
```

### **🏗️ Detailed Implementation Steps**

#### **Step 1: Infrastructure Setup**

##### **1.1 Private-GPT Installation**
```bash
# Install Private-GPT with Docker
git clone https://github.com/zylon-ai/private-gpt.git
cd private-gpt
cp .env.example .env

# Configure environment
PRIVATE_GPT_SERVER_HOST=0.0.0.0
PRIVATE_GPT_SERVER_PORT=8001
PRIVATE_GPT_SERVER_CORS_ALLOW_ORIGINS=["http://localhost:8501"]
PRIVATE_GPT_SERVER_AUTHENTICATION_GLOBAL_ENABLED=false

# Start Private-GPT
docker-compose up -d
```

##### **1.2 Ollama Setup**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama2:7b
ollama pull llama2:13b
ollama pull codellama:7b
ollama pull mistral:7b

# Configure Ollama
OLLAMA_HOST=0.0.0.0
OLLAMA_PORT=11434
```

##### **1.3 Qdrant Setup**
```bash
# Qdrant runs as part of Private-GPT
# Configure in Private-GPT .env
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=your-api-key
```

#### **Step 2: New Core Components**

##### **2.1 Private-GPT Client Wrapper**
```python
# rag/privategpt_client.py
import requests
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PrivateGPTClient:
    """Client for interacting with Private-GPT API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def health_check(self) -> bool:
        """Check if Private-GPT is running."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def ingest_file(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Ingest a file into Private-GPT."""
        try:
            # Upload file
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'text/plain')}
                response = self.session.post(
                    f"{self.base_url}/v1/ingest/file",
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                file_id = result.get('id')
                
                # Update metadata
                if file_id:
                    self.update_metadata(file_id, metadata)
                
                return file_id
            else:
                raise Exception(f"Ingestion failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            raise
    
    def query(self, question: str, collection_id: str = None, 
              top_k: int = 5, filter_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query Private-GPT with a question."""
        try:
            payload = {
                "query": question,
                "top_k": top_k,
                "collection_id": collection_id,
                "filter_metadata": filter_metadata or {}
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Query failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Error querying Private-GPT: {e}")
            raise
    
    def update_metadata(self, file_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for an ingested file."""
        try:
            response = self.session.put(
                f"{self.base_url}/v1/ingest/{file_id}/metadata",
                json=metadata
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Private-GPT."""
        try:
            response = self.session.delete(f"{self.base_url}/v1/ingest/{file_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections."""
        try:
            response = self.session.get(f"{self.base_url}/v1/ingest/list")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
```

##### **2.2 Ollama Client Integration**
```python
# rag/ollama_client.py
import requests
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama local LLMs."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate(self, model: str, prompt: str, 
                system: str = None, temperature: float = 0.7,
                max_tokens: int = 1000) -> str:
        """Generate text using Ollama model."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Generation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise
    
    def embed(self, model: str, text: str) -> List[float]:
        """Generate embeddings using Ollama model."""
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding', [])
            else:
                raise Exception(f"Embedding failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
```

##### **2.3 Qdrant Client Integration**
```python
# rag/qdrant_client.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QdrantClient:
    """Client for interacting with Qdrant vector database."""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "email_embeddings"
    
    def create_collection(self, vector_size: int = 384) -> bool:
        """Create collection for email embeddings."""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def upsert_embeddings(self, embeddings: List[Dict[str, Any]]) -> bool:
        """Upsert embeddings into Qdrant."""
        try:
            points = []
            for emb in embeddings:
                point = PointStruct(
                    id=emb['id'],
                    vector=emb['embedding'],
                    payload=emb['metadata']
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            logger.error(f"Error upserting embeddings: {e}")
            return False
    
    def search(self, query_embedding: List[float], 
               limit: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=filter_metadata
            )
            
            return [
                {
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.payload
                }
                for result in search_result
            ]
        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []
    
    def delete_embeddings(self, ids: List[str]) -> bool:
        """Delete embeddings by IDs."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}")
            return False
```

#### **Step 3: Migration of Core Components**

##### **3.1 Replace Embedder**
```python
# rag/embedder.py (REPLACE EXISTING)
import logging
from typing import List, Dict, Any, Optional
from .ollama_client import OllamaClient
from .config import settings

logger = logging.getLogger(__name__)

class LocalEmbedder:
    """Local embedding using Ollama models."""
    
    def __init__(self, model: str = "llama2:7b"):
        self.ollama_client = OllamaClient()
        self.model = model
        self.dimension = 384  # Standard for Llama2 embeddings
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = []
            for text in texts:
                embedding = self.ollama_client.embed(self.model, text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0.0] * self.dimension] * len(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            return self.ollama_client.embed(self.model, query)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return [0.0] * self.dimension
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
```

##### **3.2 Replace Generator**
```python
# rag/generator.py (REPLACE EXISTING)
import logging
from typing import List, Dict, Any, Optional
from .ollama_client import OllamaClient
from .prompts import prompt_manager
from .config import settings

logger = logging.getLogger(__name__)

class LocalGenerator:
    """Local text generation using Ollama models."""
    
    def __init__(self, model: str = "llama2:13b"):
        self.ollama_client = OllamaClient()
        self.model = model
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], 
                         sender: str = None) -> str:
        """Generate response using local LLM."""
        try:
            # Build context
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
            
            # Get prompt
            prompt = prompt_manager.get_rag_query_prompt(
                question=query,
                context_docs=context_docs,
                persona_context=""
            )
            
            # Generate response
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {e}"
    
    def generate_email_summary(self, sender: str, subject: str, 
                              date: str, content: str) -> str:
        """Generate email summary."""
        try:
            prompt = prompt_manager.get_email_summary_prompt(sender, subject, date, content)
            
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                temperature=0.3,
                max_tokens=200
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary unavailable. Email from {sender}: {subject}"
```

##### **3.3 Replace Retriever**
```python
# rag/retriever.py (REPLACE EXISTING)
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from .qdrant_client import QdrantClient
from .embedder import LocalEmbedder
from .config import settings

logger = logging.getLogger(__name__)

class LocalRetriever:
    """Local retrieval using Qdrant vector database."""
    
    def __init__(self, vector_store_dir: Path):
        self.vector_store_dir = Path(vector_store_dir)
        self.qdrant_client = QdrantClient()
        self.embedder = LocalEmbedder()
        
        # Ensure collection exists
        self.qdrant_client.create_collection(
            vector_size=self.embedder.get_embedding_dimension()
        )
    
    def build_index(self, documents: List[Dict[str, Any]], 
                   force_rebuild: bool = False) -> bool:
        """Build vector index from documents."""
        try:
            # Generate embeddings
            texts = [doc['content'] for doc in documents]
            embeddings = self.embedder.embed_texts(texts)
            
            # Prepare for Qdrant
            qdrant_docs = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                qdrant_docs.append({
                    'id': str(i),
                    'embedding': embedding,
                    'metadata': doc['metadata']
                })
            
            # Upsert to Qdrant
            success = self.qdrant_client.upsert_embeddings(qdrant_docs)
            
            if success:
                logger.info(f"Successfully indexed {len(documents)} documents")
                return True
            else:
                logger.error("Failed to upsert embeddings")
                return False
                
        except Exception as e:
            logger.error(f"Error building index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, 
               filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)
            
            # Search in Qdrant
            results = self.qdrant_client.search(
                query_embedding=query_embedding,
                limit=top_k,
                filter_metadata=filter_metadata
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
```

#### **Step 4: Email Pipeline Migration**

##### **4.1 Update Email Pipeline**
```python
# rag/email_pipeline.py (UPDATE EXISTING)
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from .privategpt_client import PrivateGPTClient
from .ollama_client import OllamaClient
from .config import settings

logger = logging.getLogger(__name__)

class LocalEmailRAGPipeline:
    """Local email RAG pipeline using Private-GPT."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.parsed_emails_dir = self.data_dir / "parsed_emails"
        self.privategpt_client = PrivateGPTClient()
        self.ollama_client = OllamaClient()
        
        # Performance tracking
        self.stats = {
            'documents_processed': 0,
            'queries_processed': 0,
            'ingestion_time': 0.0,
            'query_time': 0.0
        }
    
    def ingest_emails(self, force_rebuild: bool = False) -> bool:
        """Ingest emails into Private-GPT."""
        try:
            if not self.privategpt_client.health_check():
                logger.error("Private-GPT is not running")
                return False
            
            # Get all parsed email files
            email_files = list(self.parsed_emails_dir.glob("*.txt"))
            
            for email_file in email_files:
                # Extract metadata from filename
                metadata = self._extract_metadata_from_filename(email_file.name)
                
                # Ingest into Private-GPT
                file_id = self.privategpt_client.ingest_file(email_file, metadata)
                
                if file_id:
                    self.stats['documents_processed'] += 1
                    logger.info(f"Ingested {email_file.name} with ID {file_id}")
                else:
                    logger.error(f"Failed to ingest {email_file.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting emails: {e}")
            return False
    
    def query(self, question: str, label: str = None, 
              days_back: int = 30, sender: str = None) -> Dict[str, Any]:
        """Query the local RAG system."""
        try:
            # Build filter metadata
            filter_metadata = {}
            if label:
                filter_metadata['label'] = label
            if sender:
                filter_metadata['sender'] = sender
            
            # Query Private-GPT
            response = self.privategpt_client.query(
                question=question,
                top_k=5,
                filter_metadata=filter_metadata
            )
            
            self.stats['queries_processed'] += 1
            
            return {
                'answer': response.get('choices', [{}])[0].get('message', {}).get('content', ''),
                'sources': response.get('sources', []),
                'question': question
            }
            
        except Exception as e:
            logger.error(f"Error querying: {e}")
            return {
                'answer': f"Error processing query: {e}",
                'sources': [],
                'question': question
            }
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from email filename."""
        try:
            # Parse filename format: uuid_subject.txt
            parts = filename.replace('.txt', '').split('_', 1)
            if len(parts) == 2:
                uuid, subject = parts
                return {
                    'uuid': uuid,
                    'subject': subject.replace('-', ' '),
                    'type': 'email',
                    'source': 'parsed_emails'
                }
            return {'type': 'email', 'source': 'parsed_emails'}
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {'type': 'email', 'source': 'parsed_emails'}
```

#### **Step 5: Frontend Integration**

##### **5.1 Update Streamlit App**
```python
# frontend/app.py (UPDATE EXISTING)
# Add new imports
from rag.privategpt_client import PrivateGPTClient
from rag.ollama_client import OllamaClient

# Update query function
def query_rag(question: str, label: str = None, days_back: int = 30, sender_filter: str = None):
    """Query the local RAG system via Private-GPT."""
    try:
        # Use Private-GPT client directly
        privategpt_client = PrivateGPTClient()
        
        # Build filter metadata
        filter_metadata = {}
        if label and label != "All":
            filter_metadata['label'] = label
        if sender_filter:
            filter_metadata['sender'] = sender_filter
        
        # Query Private-GPT
        response = privategpt_client.query(
            question=question,
            top_k=5,
            filter_metadata=filter_metadata
        )
        
        return {
            'answer': response.get('choices', [{}])[0].get('message', {}).get('content', ''),
            'sources': response.get('sources', []),
            'question': question
        }
        
    except Exception as e:
        st.error(f"Error querying local RAG: {e}")
        return None

# Add health check function
def check_local_services():
    """Check if local services are running."""
    privategpt_client = PrivateGPTClient()
    ollama_client = OllamaClient()
    
    services_status = {
        'private_gpt': privategpt_client.health_check(),
        'ollama': len(ollama_client.list_models()) > 0
    }
    
    return services_status
```

#### **Step 6: Configuration Updates**

##### **6.1 Update Environment Configuration**
```python
# rag/config.py (UPDATE EXISTING)
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class LocalRAGSettings:
    """Configuration for local RAG pipeline."""
    
    # Private-GPT Settings
    PRIVATE_GPT_URL: str = os.getenv("PRIVATE_GPT_URL", "http://localhost:8001")
    PRIVATE_GPT_API_KEY: Optional[str] = os.getenv("PRIVATE_GPT_API_KEY")
    
    # Ollama Settings
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2:13b")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "llama2:7b")
    
    # Qdrant Settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "2000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    
    # Generation Settings
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Storage Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    PARSED_EMAILS_DIR: Path = DATA_DIR / "parsed_emails"
    VECTOR_STORE_DIR: Path = DATA_DIR / "vector_store"
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Update global settings
settings = LocalRAGSettings()
```

##### **6.2 Update Requirements**
```txt
# requirements.txt (UPDATE EXISTING)
# Remove cloud dependencies
# cohere>=4.0.0,<5.0.0
# google-generativeai>=0.3.0,<1.0.0
# openai>=1.86.0,<2.0.0
# faiss-cpu>=1.7.4,<2.0.0
# sentence-transformers>=2.2.0,<3.0.0

# Add local dependencies
private-gpt-client>=0.1.0
qdrant-client>=1.7.0
ollama>=0.1.0
docker-compose>=1.29.0

# Keep existing dependencies
fastapi>=0.104.0,<1.0.0
uvicorn[standard]>=0.24.0,<1.0.0
pydantic>=2.5.0,<3.0.0
streamlit>=1.28.0,<2.0.0
python-dotenv>=1.0.0,<1.1.0
requests>=2.31.0,<3.0.0
pandas==2.2.2
numpy>=1.24.0,<2.0.0
```

#### **Step 7: Docker Compose Setup**

##### **7.1 Docker Compose Configuration**
```yaml
# docker-compose.yml
version: '3.8'

services:
  private-gpt:
    image: ghcr.io/zylon-ai/private-gpt:latest
    container_name: private-gpt
    ports:
      - "8001:8001"
    environment:
      - PRIVATE_GPT_SERVER_HOST=0.0.0.0
      - PRIVATE_GPT_SERVER_PORT=8001
      - PRIVATE_GPT_SERVER_CORS_ALLOW_ORIGINS=["http://localhost:8501"]
      - PRIVATE_GPT_SERVER_AUTHENTICATION_GLOBAL_ENABLED=false
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - OLLAMA_HOST=ollama
      - OLLAMA_PORT=11434
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    depends_on:
      - qdrant
      - ollama
    networks:
      - email-rag-network

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - email-rag-network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - email-rag-network

  streamlit:
    build: .
    container_name: email-rag-frontend
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./frontend:/app/frontend
    environment:
      - PRIVATE_GPT_URL=http://private-gpt:8001
      - OLLAMA_URL=http://ollama:11434
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    depends_on:
      - private-gpt
    networks:
      - email-rag-network

volumes:
  qdrant_data:
  ollama_data:

networks:
  email-rag-network:
    driver: bridge
```

##### **7.2 Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **🚀 Migration Execution Plan**

#### **Phase 1: Infrastructure Setup (Week 1)**
1. **Day 1-2**: Install and configure Private-GPT, Ollama, Qdrant
2. **Day 3-4**: Set up Docker containers and networking
3. **Day 5**: Test basic connectivity and health checks

#### **Phase 2: Core Component Migration (Week 2)**
1. **Day 1-2**: Implement Private-GPT client wrapper
2. **Day 3-4**: Implement Ollama and Qdrant clients
3. **Day 5**: Replace embedder, generator, and retriever components

#### **Phase 3: Pipeline Integration (Week 3)**
1. **Day 1-2**: Update email pipeline for local processing
2. **Day 3-4**: Integrate with frontend and test end-to-end
3. **Day 5**: Performance optimization and error handling

#### **Phase 4: Testing & Deployment (Week 4)**
1. **Day 1-2**: Comprehensive testing of offline functionality
2. **Day 3-4**: Performance benchmarking and optimization
3. **Day 5**: Production deployment and monitoring setup

### **⚠️ Risks & Mitigation**

#### **Technical Risks**
1. **Model Performance**: Local models may be slower/less accurate
   - **Mitigation**: Use larger models (13B+), implement caching
2. **Resource Requirements**: Higher CPU/RAM usage
   - **Mitigation**: Optimize model loading, implement resource limits
3. **Dependency Conflicts**: New dependencies may conflict
   - **Mitigation**: Use virtual environments, pin versions

#### **Operational Risks**
1. **Service Availability**: Local services may fail
   - **Mitigation**: Health checks, auto-restart, fallback modes
2. **Data Loss**: Local storage risks
   - **Mitigation**: Regular backups, data validation
3. **User Experience**: Slower response times
   - **Mitigation**: Async processing, progress indicators

### **✅ Acceptance Criteria**

#### **Functional Requirements**
- [ ] All AI chat features work 100% offline
- [ ] Email ingestion and processing works locally
- [ ] Vector search and retrieval functions properly
- [ ] Response generation quality matches or exceeds cloud version
- [ ] No data leaves the local environment

#### **Performance Requirements**
- [ ] Query response time < 5 seconds
- [ ] Ingestion processing time < 30 seconds per email
- [ ] Memory usage < 8GB for typical workloads
- [ ] CPU usage < 80% during peak operations

#### **Reliability Requirements**
- [ ] 99.9% uptime for local services
- [ ] Graceful degradation when services fail
- [ ] Automatic recovery from common failures
- [ ] Comprehensive error logging and monitoring

---

## 📚 **Additional Resources**

- [Private-GPT Documentation](https://docs.privategpt.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [ChatWise Features](https://chatwise.app/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 🤝 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: [Project Wiki](link-to-wiki)
- **Enterprise Support**: enterprise@your-domain.com

---

**Built with ❤️ for privacy-first AI email processing**

## 🔐 Data Privacy & Security

### 🛡️ How We Protect Your Data

**Your privacy is our top priority.** Here's exactly how we ensure your emails and documents remain completely private and secure:

### 🔒 Data Privacy Guarantees

#### **100% Private Processing**
```
✅ Your emails are processed in isolated environments
✅ Each user's data is completely separated
✅ No cross-user data access or sharing
✅ AI models only see your data, never others'
```

#### **Zero Data Sharing**
```
✅ We never sell your data to third parties
✅ We never share your emails with advertisers
✅ We never use your data for training other AI models
✅ We never access your data for any purpose other than serving you
```

#### **Complete Data Control**
```
✅ You own all your data
✅ Export your data anytime
✅ Delete your data completely
✅ Control what gets processed
```

### 🏗️ Technical Security Measures

#### **Data Encryption**
```
🔐 End-to-End Encryption
- All data encrypted in transit (HTTPS/TLS 1.3)
- All data encrypted at rest (AES-256)
- Database encryption with customer-managed keys
- File-level encryption for all uploads

🔐 Encryption Keys
- Unique encryption keys per user
- Keys never stored with data
- Hardware Security Modules (HSM) for key management
- Automatic key rotation every 90 days
```

#### **Infrastructure Security**
```
🛡️ Cloud Security
- SOC 2 Type II certified infrastructure
- ISO 27001 compliant data centers
- Regular security audits and penetration testing
- 24/7 security monitoring and threat detection

🛡️ Network Security
- Private network isolation
- Firewall protection at multiple layers
- DDoS protection and mitigation
- Intrusion detection and prevention systems
```

#### **Application Security**
```
🔒 Code Security
- Regular security code reviews
- Automated vulnerability scanning
- Dependency vulnerability monitoring
- Secure development lifecycle (SDL)

🔒 Access Control
- Multi-factor authentication (MFA) required
- Role-based access control (RBAC)
- Session management and timeout
- Audit logging for all access
```

### 📊 Data Flow & Processing

#### **How Your Data Moves**
```
1. Email Forwarding → Encrypted HTTPS → Secure Server
2. Secure Server → Isolated Processing → Private-GPT
3. Private-GPT → Local Processing → Encrypted Storage
4. Encrypted Storage → Secure Retrieval → Your Browser
```

#### **Data Processing Isolation**
```
👤 User Isolation
- Separate database schemas per user
- Isolated Private-GPT instances
- Dedicated vector storage collections
- No data leakage between users

🔒 Processing Isolation
- Containerized processing environments
- Memory isolation between users
- Temporary data cleanup after processing
- No persistent cross-user data storage
```

### 🏢 Compliance & Certifications

#### **Regulatory Compliance**
```
📋 GDPR Compliance
- Right to be forgotten (data deletion)
- Data portability (export functionality)
- Consent management
- Privacy by design implementation

📋 SOC 2 Type II
- Security, availability, and confidentiality
- Annual third-party audits
- Continuous monitoring and reporting
- Incident response procedures

📋 ISO 27001
- Information security management
- Risk assessment and treatment
- Security controls and procedures
- Regular compliance audits
```