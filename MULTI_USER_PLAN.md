# Multi-User Email RAG System Plan

## Current State (Single User)
- Single Gmail account: `mandipinder@gmail.com`
- Local deployment only
- No user authentication
- Single API key set

## Target State (Multi User)
- Multiple Gmail accounts
- Web-based access
- User authentication
- Separate email data per user
- Shared AI provider costs

## Implementation Plan

### Phase 1: Add User Authentication
1. **User Registration/Login System**
   - Email/password authentication
   - JWT tokens for sessions
   - User profile management

2. **Database Schema Changes**
   ```sql
   -- Users table
   CREATE TABLE users (
       id INTEGER PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- User email accounts
   CREATE TABLE user_email_accounts (
       id INTEGER PRIMARY KEY,
       user_id INTEGER REFERENCES users(id),
       gmail_email TEXT NOT NULL,
       gmail_app_password TEXT NOT NULL,
       gmail_label TEXT DEFAULT 'substackrag',
       is_active BOOLEAN DEFAULT true,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Email data with user isolation
   ALTER TABLE emails ADD COLUMN user_id INTEGER REFERENCES users(id);
   ALTER TABLE personas ADD COLUMN user_id INTEGER REFERENCES users(id);
   ```

### Phase 2: Multi-Email Account Support
1. **Email Account Management**
   - Users can add their own Gmail accounts
   - Secure storage of app passwords
   - Email account status monitoring

2. **Separate Email Processing**
   - Each user's emails processed separately
   - Isolated vector stores per user
   - User-specific RAG queries

### Phase 3: Web Interface Updates
1. **User Dashboard**
   - Email account management
   - Email processing status
   - Usage statistics

2. **Query Interface**
   - User-specific email search
   - Personal email insights
   - Shared vs private queries

### Phase 4: Deployment & Scaling
1. **Cloud Deployment**
   - Deploy to Render/Railway/DigitalOcean
   - Database migration
   - Environment configuration

2. **Cost Management**
   - Shared AI provider costs
   - Usage tracking per user
   - Rate limiting

## Technical Implementation

### Backend Changes
```python
# Add user authentication middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# User model
class User:
    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # Verify JWT token and return user
    pass

# Protected endpoints
@app.post("/query")
async def query_emails(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    # Only return emails for current user
    pass
```

### Frontend Changes
```javascript
// Add login/register pages
// Add user dashboard
// Add email account management
// Update query interface for user isolation
```

## Deployment Options

### Option A: Shared Instance
- Single server, multiple users
- Shared AI provider costs
- Lower cost per user

### Option B: Multi-Tenant
- Separate databases per user
- Better isolation
- Higher cost per user

### Option C: Self-Hosted
- Users deploy their own instances
- Complete isolation
- Higher setup complexity

## Cost Considerations

### AI Provider Costs
- Shared across all users
- Rate limiting per user
- Usage monitoring

### Infrastructure Costs
- Server hosting
- Database storage
- Bandwidth

### Pricing Model Options
1. **Freemium**: Basic features free, premium paid
2. **Per-user**: Monthly fee per user
3. **Usage-based**: Pay per query/email processed

## Security Considerations

### Data Isolation
- User emails completely separated
- No cross-user data access
- Encrypted storage

### Authentication
- Secure password hashing
- JWT token management
- Session timeout

### Email Security
- Secure app password storage
- Encrypted email processing
- Audit logging

## Migration Strategy

### Phase 1: Authentication (Week 1-2)
- Add user system
- Deploy to cloud
- Test with single user

### Phase 2: Multi-Email (Week 3-4)
- Add email account management
- Test with multiple accounts
- Data migration

### Phase 3: Polish (Week 5-6)
- UI improvements
- Performance optimization
- Documentation

## Success Metrics

### User Adoption
- Number of registered users
- Active users per month
- Email accounts per user

### System Performance
- Query response time
- Email processing speed
- System uptime

### Cost Efficiency
- Cost per user
- AI provider usage
- Infrastructure costs 