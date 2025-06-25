# Email RAG Assistant - Developer Guide

A comprehensive guide for recreating this email RAG (Retrieval-Augmented Generation) system in JavaScript/TypeScript or integrating it into existing JS/TS projects.

## 🎯 Overview

This email RAG system processes emails from Gmail (specifically Substack newsletters), extracts content, creates embeddings, and provides intelligent Q&A capabilities using AI. The system includes:

- **Email Processing**: Gmail API integration with filtering
- **Content Extraction**: Parsing email content and metadata
- **Vector Database**: FAISS-based similarity search
- **RAG Pipeline**: Cohere embeddings + generation
- **Web Interface**: Multi-pane notebook-style UI
- **Persona Detection**: AI-powered sender analysis

## 🏗️ Architecture

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
```

## 🚀 Quick Start - JavaScript/TypeScript Implementation

### 1. Project Setup

```bash
# Create new project
mkdir email-rag-js
cd email-rag-js
npm init -y

# Install dependencies
npm install express cors dotenv googleapis cohere-ai faiss-node sqlite3
npm install -D typescript @types/node @types/express @types/cors
npm install -D nodemon ts-node

# Initialize TypeScript
npx tsc --init
```

### 2. Core Dependencies

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "googleapis": "^128.0.0",
    "cohere-ai": "^5.0.0",
    "faiss-node": "^0.5.0",
    "sqlite3": "^5.1.6",
    "node-cron": "^3.0.3"
  },
  "devDependencies": {
    "typescript": "^5.2.2",
    "@types/node": "^20.8.0",
    "@types/express": "^4.17.20",
    "@types/cors": "^2.8.15",
    "nodemon": "^3.0.1",
    "ts-node": "^10.9.1"
  }
}
```

### 3. Environment Configuration

```env
# .env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_CLIENT_ID=your-google-client-id
GMAIL_CLIENT_SECRET=your-google-client-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
COHERE_API_KEY=your-cohere-api-key
GMAIL_LABEL=substackrag
```

### 4. Project Structure

```
email-rag-js/
├── src/
│   ├── config/
│   │   ├── database.ts
│   │   ├── gmail.ts
│   │   └── cohere.ts
│   ├── services/
│   │   ├── emailService.ts
│   │   ├── ragService.ts
│   │   └── personaService.ts
│   ├── models/
│   │   ├── Email.ts
│   │   └── Persona.ts
│   ├── utils/
│   │   ├── parser.ts
│   │   └── embedder.ts
│   ├── routes/
│   │   ├── emails.ts
│   │   └── query.ts
│   └── app.ts
├── data/
│   ├── emails.db
│   ├── vector-store/
│   └── parsed-emails/
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
└── .env
```

## 🔧 Core Components Implementation

### 1. Email Service (Gmail Integration)

```typescript
// src/services/emailService.ts
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';

export class EmailService {
  private gmail: any;
  private oauth2Client: OAuth2Client;

  constructor() {
    this.oauth2Client = new OAuth2Client(
      process.env.GMAIL_CLIENT_ID,
      process.env.GMAIL_CLIENT_SECRET
    );
    this.oauth2Client.setCredentials({
      refresh_token: process.env.GMAIL_REFRESH_TOKEN
    });
    this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
  }

  async fetchEmails(label: string, maxResults: number = 100): Promise<Email[]> {
    try {
      const response = await this.gmail.users.messages.list({
        userId: 'me',
        labelIds: [label],
        maxResults
      });

      const emails: Email[] = [];
      for (const message of response.data.messages || []) {
        const email = await this.getEmailDetails(message.id);
        if (email) emails.push(email);
      }

      return emails;
    } catch (error) {
      console.error('Error fetching emails:', error);
      return [];
    }
  }

  private async getEmailDetails(messageId: string): Promise<Email | null> {
    try {
      const response = await this.gmail.users.messages.get({
        userId: 'me',
        id: messageId
      });

      const headers = response.data.payload?.headers;
      const subject = headers?.find(h => h.name === 'Subject')?.value || '';
      const from = headers?.find(h => h.name === 'From')?.value || '';
      const date = headers?.find(h => h.name === 'Date')?.value || '';

      // Extract content
      const content = this.extractContent(response.data.payload);

      return {
        id: messageId,
        subject,
        from,
        date: new Date(date),
        content,
        label: 'substack.com'
      };
    } catch (error) {
      console.error('Error getting email details:', error);
      return null;
    }
  }

  private extractContent(payload: any): string {
    // Implementation for extracting email content
    // Handle different MIME types (text/plain, text/html, multipart)
    return '';
  }
}
```

### 2. RAG Service (Cohere Integration)

```typescript
// src/services/ragService.ts
import cohere from 'cohere-ai';
import { Database } from 'sqlite3';

export class RAGService {
  private db: Database;

  constructor() {
    cohere.init(process.env.COHERE_API_KEY!);
    this.db = new Database('data/emails.db');
  }

  async query(question: string, label?: string, daysBack: number = 30): Promise<RAGResponse> {
    try {
      // 1. Retrieve relevant documents
      const documents = await this.retrieveDocuments(question, label, daysBack);
      
      // 2. Create embeddings for question
      const questionEmbedding = await this.createEmbedding(question);
      
      // 3. Find similar documents
      const similarDocs = await this.findSimilarDocuments(questionEmbedding, documents);
      
      // 4. Generate response
      const response = await this.generateResponse(question, similarDocs);
      
      return {
        answer: response,
        documents: similarDocs,
        question
      };
    } catch (error) {
      console.error('Error in RAG query:', error);
      throw error;
    }
  }

  private async createEmbedding(text: string): Promise<number[]> {
    const response = await cohere.embed({
      texts: [text],
      model: 'embed-english-v3.0',
      inputType: 'search_document'
    });
    return response.embeddings[0];
  }

  private async generateResponse(question: string, documents: Document[]): Promise<string> {
    const context = documents.map(doc => doc.content).join('\n\n');
    
    const response = await cohere.generate({
      model: 'command',
      prompt: `Based on the following context, answer the question. If you cannot answer from the context, say so.

Context:
${context}

Question: ${question}

Answer:`,
      maxTokens: 1000,
      temperature: 0.7
    });

    return response.generations[0].text;
  }

  private async retrieveDocuments(question: string, label?: string, daysBack: number = 30): Promise<Document[]> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysBack);

    return new Promise((resolve, reject) => {
      const query = label 
        ? 'SELECT * FROM emails WHERE label = ? AND date >= ? ORDER BY date DESC LIMIT 100'
        : 'SELECT * FROM emails WHERE date >= ? ORDER BY date DESC LIMIT 100';
      
      const params = label ? [label, cutoffDate.toISOString()] : [cutoffDate.toISOString()];
      
      this.db.all(query, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows.map(row => ({
          id: row.id,
          content: row.content,
          subject: row.subject,
          from: row.from,
          date: row.date,
          score: 0
        })));
      });
    });
  }

  private async findSimilarDocuments(embedding: number[], documents: Document[]): Promise<Document[]> {
    // Implement similarity search using FAISS or cosine similarity
    // For simplicity, return top 5 documents
    return documents.slice(0, 5);
  }
}
```

### 3. Database Service

```typescript
// src/config/database.ts
import { Database } from 'sqlite3';

export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('data/emails.db');
    this.initDatabase();
  }

  private initDatabase(): void {
    this.db.serialize(() => {
      this.db.run(`
        CREATE TABLE IF NOT EXISTS emails (
          id TEXT PRIMARY KEY,
          subject TEXT NOT NULL,
          sender TEXT NOT NULL,
          date TEXT NOT NULL,
          label TEXT NOT NULL,
          content TEXT,
          timestamp TEXT NOT NULL,
          parsed_path TEXT NOT NULL,
          has_attachments BOOLEAN DEFAULT FALSE,
          attachment_count INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.run('CREATE INDEX IF NOT EXISTS idx_label ON emails(label)');
      this.db.run('CREATE INDEX IF NOT EXISTS idx_date ON emails(date)');
      this.db.run('CREATE INDEX IF NOT EXISTS idx_sender ON emails(sender)');
    });
  }

  async insertEmail(email: Email): Promise<boolean> {
    return new Promise((resolve, reject) => {
      this.db.run(`
        INSERT OR REPLACE INTO emails (
          id, subject, sender, date, label, content, timestamp, parsed_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        email.id, email.subject, email.from, email.date.toISOString(),
        email.label, email.content, new Date().toISOString(), ''
      ], (err) => {
        if (err) reject(err);
        else resolve(true);
      });
    });
  }

  async getEmailsByLabel(label: string, daysBack: number = 30): Promise<Email[]> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysBack);

    return new Promise((resolve, reject) => {
      this.db.all(`
        SELECT * FROM emails 
        WHERE label = ? AND date >= ? 
        ORDER BY date DESC LIMIT 100
      `, [label, cutoffDate.toISOString()], (err, rows) => {
        if (err) reject(err);
        else resolve(rows.map(row => ({
          id: row.id,
          subject: row.subject,
          from: row.sender,
          date: new Date(row.date),
          content: row.content,
          label: row.label
        })));
      });
    });
  }
}
```

### 4. Express API Server

```typescript
// src/app.ts
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { emailRoutes } from './routes/emails';
import { queryRoutes } from './routes/query';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Routes
app.use('/api/emails', emailRoutes);
app.use('/api/query', queryRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Email RAG API running on port ${PORT}`);
});
```

### 5. API Routes

```typescript
// src/routes/emails.ts
import { Router } from 'express';
import { EmailService } from '../services/emailService';
import { DatabaseService } from '../config/database';

const router = Router();
const emailService = new EmailService();
const dbService = new DatabaseService();

router.get('/', async (req, res) => {
  try {
    const { label, days_back = 30 } = req.query;
    const emails = await dbService.getEmailsByLabel(label as string, Number(days_back));
    res.json({ emails });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch emails' });
  }
});

router.get('/labels', async (req, res) => {
  try {
    const labels = ['substack.com']; // Filtered to substack only
    res.json({ labels });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch labels' });
  }
});

export { router as emailRoutes };
```

```typescript
// src/routes/query.ts
import { Router } from 'express';
import { RAGService } from '../services/ragService';

const router = Router();
const ragService = new RAGService();

router.post('/', async (req, res) => {
  try {
    const { question, label, days_back = 30, sender_filter } = req.body;
    
    const response = await ragService.query(question, label, days_back);
    
    res.json({
      answer: response.answer,
      documents: response.documents,
      question: response.question
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to process query' });
  }
});

export { router as queryRoutes };
```

## 🎨 Frontend Implementation

### React/Next.js Frontend

```typescript
// components/EmailRAG.tsx
import React, { useState, useEffect } from 'react';
import { Email, RAGResponse } from '../types';

interface EmailRAGProps {
  apiUrl: string;
}

export const EmailRAG: React.FC<EmailRAGProps> = ({ apiUrl }) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    try {
      const response = await fetch(`${apiUrl}/emails?label=substack.com`);
      const data = await response.json();
      setEmails(data.emails);
    } catch (error) {
      console.error('Error fetching emails:', error);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          label: 'substack.com',
          days_back: 30
        })
      });
      
      const data = await response.json();
      setResponse(data);
    } catch (error) {
      console.error('Error querying RAG:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="email-rag-container">
      <div className="sidebar">
        <h3>📧 Substack Emails ({emails.length})</h3>
        <div className="email-list">
          {emails.map(email => (
            <div key={email.id} className="email-item">
              <h4>{email.subject}</h4>
              <p>From: {email.from}</p>
              <p>Date: {new Date(email.date).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      </div>
      
      <div className="main-content">
        <div className="query-section">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your emails..."
            rows={3}
          />
          <button onClick={handleQuery} disabled={loading}>
            {loading ? 'Thinking...' : 'Ask Question'}
          </button>
        </div>
        
        {response && (
          <div className="response-section">
            <h3>Answer:</h3>
            <p>{response.answer}</p>
            
            <h4>Sources:</h4>
            <div className="sources">
              {response.documents.map((doc, index) => (
                <div key={index} className="source-item">
                  <h5>{doc.subject}</h5>
                  <p>From: {doc.from}</p>
                  <p>{doc.content.substring(0, 200)}...</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
```

## 🔄 Integration with Existing Projects

### 1. Add to Existing Express App

```typescript
// In your existing Express app
import { emailRoutes } from './email-rag/routes/emails';
import { queryRoutes } from './email-rag/routes/query';

// Add routes to your existing app
app.use('/api/email-rag/emails', emailRoutes);
app.use('/api/email-rag/query', queryRoutes);
```

### 2. React Component Integration

```typescript
// In your React app
import { EmailRAG } from './components/EmailRAG';

function App() {
  return (
    <div className="App">
      <h1>My App</h1>
      <EmailRAG apiUrl="http://localhost:3000/api/email-rag" />
    </div>
  );
}
```

### 3. Next.js API Route Integration

```typescript
// pages/api/email-rag/query.ts
import { NextApiRequest, NextApiResponse } from 'next';
import { RAGService } from '../../../services/ragService';

const ragService = new RAGService();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { question, label, days_back = 30 } = req.body;
    const response = await ragService.query(question, label, days_back);
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Failed to process query' });
  }
}
```

## 🚀 Deployment

### 1. Docker Setup

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### 2. Environment Variables

```env
# Production .env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_CLIENT_ID=your-google-client-id
GMAIL_CLIENT_SECRET=your-google-client-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
COHERE_API_KEY=your-cohere-api-key
GMAIL_LABEL=substackrag
NODE_ENV=production
PORT=3000
```

### 3. Deployment Scripts

```json
{
  "scripts": {
    "dev": "nodemon src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "deploy": "npm run build && docker build -t email-rag . && docker run -p 3000:3000 email-rag"
  }
}
```

## 🔧 Configuration & Customization

### 1. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and set environment variables

### 2. Cohere API Setup

1. Sign up at [Cohere](https://cohere.ai/)
2. Get your API key
3. Set `COHERE_API_KEY` environment variable

### 3. Custom Email Filters

```typescript
// Custom email filtering
const customFilter = (email: Email): boolean => {
  // Filter by domain
  const domain = email.from.split('@')[1];
  return domain === 'substack.com';
  
  // Filter by subject keywords
  const keywords = ['newsletter', 'update', 'digest'];
  return keywords.some(keyword => 
    email.subject.toLowerCase().includes(keyword)
  );
};
```

## 📊 Performance Optimization

### 1. Caching

```typescript
import NodeCache from 'node-cache';

const cache = new NodeCache({ stdTTL: 3600 }); // 1 hour

// Cache email embeddings
const getCachedEmbedding = async (text: string): Promise<number[]> => {
  const key = `embedding:${text}`;
  let embedding = cache.get<number[]>(key);
  
  if (!embedding) {
    embedding = await createEmbedding(text);
    cache.set(key, embedding);
  }
  
  return embedding;
};
```

### 2. Batch Processing

```typescript
// Process emails in batches
const processEmailsBatch = async (emails: Email[], batchSize: number = 10) => {
  const batches = [];
  for (let i = 0; i < emails.length; i += batchSize) {
    batches.push(emails.slice(i, i + batchSize));
  }
  
  for (const batch of batches) {
    await Promise.all(batch.map(email => processEmail(email)));
    await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
  }
};
```

## 🧪 Testing

### 1. Unit Tests

```typescript
// tests/ragService.test.ts
import { RAGService } from '../src/services/ragService';

describe('RAGService', () => {
  let ragService: RAGService;

  beforeEach(() => {
    ragService = new RAGService();
  });

  test('should generate response for valid question', async () => {
    const response = await ragService.query('What are the latest AI trends?');
    expect(response.answer).toBeDefined();
    expect(response.documents).toBeInstanceOf(Array);
  });
});
```

### 2. Integration Tests

```typescript
// tests/integration.test.ts
import request from 'supertest';
import app from '../src/app';

describe('Email RAG API', () => {
  test('GET /api/emails should return emails', async () => {
    const response = await request(app)
      .get('/api/emails?label=substack.com')
      .expect(200);
    
    expect(response.body.emails).toBeInstanceOf(Array);
  });

  test('POST /api/query should return RAG response', async () => {
    const response = await request(app)
      .post('/api/query')
      .send({
        question: 'What are the latest AI trends?',
        label: 'substack.com'
      })
      .expect(200);
    
    expect(response.body.answer).toBeDefined();
  });
});
```

## 🔒 Security Considerations

### 1. API Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

### 2. Input Validation

```typescript
import Joi from 'joi';

const querySchema = Joi.object({
  question: Joi.string().min(1).max(1000).required(),
  label: Joi.string().optional(),
  days_back: Joi.number().min(1).max(365).default(30)
});

// In route handler
const { error, value } = querySchema.validate(req.body);
if (error) {
  return res.status(400).json({ error: error.details[0].message });
}
```

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Cohere API Documentation](https://docs.cohere.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Express.js Documentation](https://expressjs.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Happy coding! 🚀**

This guide provides a complete foundation for implementing the email RAG system in JavaScript/TypeScript. The modular architecture makes it easy to integrate into existing projects or build from scratch. 