# AI Mental Health Chatbot - Architecture Overview

## System Architecture

The Mental Health Chatbot platform follows a microservices architecture pattern with clear separation of concerns:

### High-Level Architecture

```
┌─────────────────┐
│   React SPA     │◄─── User Interface
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  Nginx Proxy    │◄─── Reverse Proxy & Load Balancer
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌──▼───┐
│Flask │   │Node  │
│ API  │   │Socket│◄─── Real-time Communication
└───┬──┘   └──┬───┘
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │ Redis   │◄─── Cache & Message Queue
    └─────────┘
         │
    ┌────▼────┐
    │PostgreSQL│◄─── Primary Database
    └─────────┘
```

## Core Components

### 1. Frontend (React)
- **Technology**: React 18, React Router, Axios, Socket.IO Client
- **Responsibilities**:
  - User authentication and session management
  - Chat interface with real-time updates
  - Mood tracking and journaling
  - Mental health screening tools
  - Admin dashboard for clinicians
- **State Management**: React hooks (useState, useEffect, useContext)
- **Styling**: CSS custom properties, responsive design

### 2. Backend API (Flask)
- **Technology**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Responsibilities**:
  - REST API endpoints for all operations
  - User authentication and authorization
  - Business logic for mental health features
  - AI integration layer
  - Crisis detection and intervention
- **Key Services**:
  - `ai_connector.py`: Multi-provider AI integration (Gemini, OpenAI, Anthropic, Groq)
  - `moderation.py`: Crisis keyword detection and risk assessment
  - `rag.py`: Mental health resource retrieval
  - `notification.py`: Email/SMS alerts

### 3. Real-time Service (Node.js + Socket.IO)
- **Technology**: Node.js, Socket.IO, Redis
- **Responsibilities**:
  - WebSocket connections for live chat
  - Typing indicators
  - Presence management (online/offline)
  - Message broadcasting
  - Admin alerts for crisis situations

### 4. Database Layer
- **Primary Database**: PostgreSQL
- **Schema**:
  - `users`: Authentication and profile data
  - `conversations`: Chat sessions
  - `messages`: Individual messages with sentiment analysis
  - `mood_logs`: Daily mood tracking
  - `screening_results`: PHQ-9, GAD-7 assessments
  - `admin_notes`: Clinician observations
- **Vector Database**: ChromaDB for RAG (mental health resources)

### 5. Cache & Queue (Redis)
- **Uses**:
  - Session storage
  - Real-time message queue
  - Celery task queue
  - Rate limiting
  - Cached AI responses

## Data Flow

### Chat Message Flow
1. User types message in React frontend
2. Frontend sends POST request to `/api/chat/message`
3. Flask backend:
   - Analyzes message for crisis keywords (moderation service)
   - Retrieves conversation history from PostgreSQL
   - Sends to AI provider (Gemini/OpenAI/etc.)
   - Stores user message and AI response in database
   - Updates risk level if needed
4. Backend returns response to frontend
5. Socket.IO broadcasts message for real-time updates
6. If crisis detected, triggers admin notification

### Crisis Intervention Flow
1. Message contains crisis keywords
2. Moderation service flags message (HIGH/CRITICAL risk)
3. User receives immediate crisis resources (hotline numbers)
4. Admin notification sent via email/SMS
5. Conversation flagged for review
6. User's risk level updated in database

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Access + Refresh token pattern
- **Token Storage**: LocalStorage (frontend), HTTP-only cookies option
- **Role-Based Access Control**: User, Admin, Clinician roles
- **Password Security**: bcrypt hashing with salt

### Data Protection
- **In Transit**: TLS/SSL for all communications
- **At Rest**: Database encryption, encrypted backups
- **PII Handling**: Minimal collection, anonymization where possible
- **GDPR Compliance**: Data export and deletion endpoints

### API Security
- **Rate Limiting**: Per-user, per-IP limits via Flask-Limiter
- **CORS**: Configured for specific origins
- **Input Validation**: Marshmallow schemas
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries

## AI Integration Architecture

### Multi-Provider Support
The system supports multiple AI providers through a unified interface:

```python
AIConnector
├── Gemini (Google Generative AI)
├── OpenAI (GPT-4, GPT-3.5)
├── Anthropic (Claude 3)
├── Groq (Fast inference)
└── Local LLMs (Ollama, LM Studio)
```

**Provider Selection**: Environment variable `AI_PROVIDER=gemini`

### RAG (Retrieval Augmented Generation)
- **Vector Database**: ChromaDB with sentence-transformers embeddings
- **Knowledge Base**: CBT/DBT techniques, coping strategies, crisis resources
- **Query Flow**:
  1. User message embedded into vector
  2. Similar resources retrieved from vector DB
  3. Resources injected into AI prompt context
  4. AI generates evidence-based response

## Deployment Architecture

### Docker Containers
- `backend`: Flask API
- `realtime`: Node.js Socket.IO server
- `frontend`: React build served by Nginx
- `postgres`: PostgreSQL database
- `redis`: Redis cache
- `celery-worker`: Background tasks
- `celery-beat`: Scheduled tasks
- `nginx`: Reverse proxy

### Kubernetes (Production)
- **Deployments**: Separate for each service
- **Services**: ClusterIP for internal, LoadBalancer for external
- **Ingress**: HTTPS termination, routing
- **Secrets**: API keys, database credentials
- **ConfigMaps**: Environment configuration
- **Persistent Volumes**: Database data, uploads

## Scalability Considerations

### Horizontal Scaling
- Flask backend: Stateless, can scale to multiple replicas
- Socket.IO: Sticky sessions required, Redis adapter for multi-instance
- Database: Read replicas for analytics queries

### Performance Optimization
- **Caching**: Redis for frequently accessed data
- **CDN**: Static assets (frontend)
- **Database Indexing**: On user_id, conversation_id, created_at
- **Connection Pooling**: SQLAlchemy pool for database connections

## Monitoring & Logging

### Application Monitoring
- **Health Checks**: `/health` endpoint for all services
- **Metrics**: Response times, error rates, active users
- **Logging**: Structured JSON logs

### Crisis Monitoring
- **Real-time Alerts**: Admin dashboard for flagged conversations
- **Email/SMS Notifications**: Immediate alerts for CRITICAL risk
- **Audit Trail**: All crisis interventions logged

## Future Enhancements

1. **Voice Support**: Speech-to-text and text-to-speech integration
2. **Multi-language**: i18n translation service
3. **Mobile Apps**: React Native iOS/Android
4. **Analytics Dashboard**: Trend analysis for admins
5. **Teletherapy Integration**: Video calling with licensed therapists
6. **Peer Support Groups**: Moderated group chat rooms

---

**Built with care for mental health support** 💙
