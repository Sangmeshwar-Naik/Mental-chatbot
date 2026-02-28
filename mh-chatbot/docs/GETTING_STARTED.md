# Getting Started Guide

## Prerequisites

Before you begin, ensure you have:
- Python 3.10 or higher
- Node.js 16 or higher
- PostgreSQL or SQLite
- Redis
- Docker and Docker Compose (recommended)

## Option 1: Docker Compose (Recommended)

### 1. Clone and Configure

```bash
cd mh-chatbot
cp backend-flask/.env.example backend-flask/.env
```

### 2. Edit Environment Variables

Open `backend-flask/.env` and add your API keys:

```env
# AI Provider (choose one)
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here

# Or use OpenAI
# AI_PROVIDER=openai
# OPENAI_API_KEY=your-openai-key-here

# Database
DATABASE_URL=postgresql://mh_user:changeme123@postgres:5432/mental_health_db

# Secret Keys
SECRET_KEY=generate-a-strong-random-key
JWT_SECRET_KEY=generate-another-strong-key
```

### 3. Start All Services

```bash
cd infra
docker-compose up -d
```

### 4. Create Admin User

```bash
docker exec -it mh-backend python ../scripts/create_admin.py
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **Socket.IO**: http://localhost:3001

## Option 2: Manual Setup

### Backend Setup

```bash
cd backend-flask

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python app.py
# Database tables will be created automatically

# Create admin user
python ../scripts/create_admin.py
```

### Node.js Real-time Service

```bash
cd node-services/realtime
npm install
npm start
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Getting Your API Keys

### Google Gemini
1. Visit https://makersuite.google.com/app/apikey
2. Create new project or use existing
3. Create API key
4. Copy key to `.env` as `GEMINI_API_KEY`

### OpenAI (Alternative)
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env` as `OPENAI_API_KEY`

## First Login

1. Navigate to http://localhost:3000
2. Click "Register"
3. Create your account
4. Start chatting!

## Troubleshooting

### "Cannot connect to database"
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- For Docker: `docker-compose logs postgres`

### "AI provider error"
- Verify API key is correct
- Check API_PROVIDER matches your key (gemini/openai/etc.)
- Review backend logs: `docker-compose logs backend`

### "Socket connection failed"
- Ensure real-time service is running on port 3001
- Check REACT_APP_SOCKET_URL in frontend

## Next Steps

- Read the [Architecture Documentation](./architecture.md)
- Review [Safety Policy](./safety_policy.md)
- Check [API Documentation](./api.md)

## Support

For issues or questions:
- GitHub Issues: [Link to repo]
- Email: support@example.com

---

**Remember**: This is a demonstration platform. For production use with real patients, ensure proper HIPAA/GDPR compliance, clinical oversight, and legal review.
