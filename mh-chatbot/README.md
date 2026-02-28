# AI Mental Health Chatbot Platform

A comprehensive mental health support platform featuring AI-powered conversations, real-time chat, clinical screening tools, and multilingual support.

## 🌟 Features

### Core Features
- **AI-Powered Chat**: Empathetic conversations using Google Gemini, OpenAI, or Anthropic
- **Real-time Messaging**: Socket.IO for instant communication
- **Crisis Detection**: Automatic detection of high-risk conversations with admin alerts
- **Clinical Screenings**: PHQ-9 (depression), GAD-7 (anxiety) assessments
- **Mood Tracking**: Daily mood logging with trend analysis
- **Multi-language Support**: i18n translation service
- **Voice Support**: Speech-to-Text and Text-to-Speech capabilities

### Safety & Privacy
- End-to-end encryption for sensitive data
- HIPAA/GDPR compliance considerations
- Crisis intervention protocols
- Content moderation and filtering
- Secure authentication with JWT tokens

## 🏗️ Architecture

```
Frontend (React) ←→ Nginx ←→ Flask Backend API
                              ↓
                         PostgreSQL
                              ↓
    Node.js Services ←→ Redis ←→ Celery Workers
    (Socket.IO, i18n, STT/TTS)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL (or SQLite for development)
- Redis
- Docker & Docker Compose (optional)

### Installation

#### 1. Clone the repository
```bash
git clone <repository-url>
cd mh-chatbot
```

#### 2. Backend Setup
```bash
cd backend-flask
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and configuration

# Initialize database
python manage.py db init
python manage.py db migrate
python manage.py db upgrade

# Create admin user
python ../scripts/create_admin.py

# Run Flask server
python app.py
```

#### 3. Node.js Services Setup
```bash
# Real-time service
cd node-services/realtime
npm install
npm start

# Translation service
cd ../i18n
npm install
npm start

# STT/TTS service
cd ../stt_tts
npm install
npm start
```

#### 4. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Docker Deployment (Recommended)
```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api
- API Documentation: http://localhost:5000/api/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in `backend-flask/`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=postgresql://user:password@localhost:5432/mental_health_db

# AI Provider (choose one)
AI_PROVIDER=gemini  # Options: gemini, openai, anthropic, groq
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Twilio (for SMS crisis alerts)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Crisis hotline numbers
CRISIS_HOTLINE_US=988
CRISIS_HOTLINE_INTERNATIONAL=+1-800-273-8255
```

## 📚 API Documentation

See [docs/api.md](docs/api.md) for complete API reference.

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh JWT token

**Chat**
- `POST /api/chat/message` - Send message and get AI response
- `GET /api/chat/history` - Get conversation history
- `DELETE /api/chat/conversation/:id` - Delete conversation

**Screenings**
- `POST /api/screenings/phq9` - Submit PHQ-9 screening
- `POST /api/screenings/gad7` - Submit GAD-7 screening
- `GET /api/screenings/history` - View screening results

**User**
- `GET /api/user/profile` - Get user profile
- `POST /api/user/mood` - Log daily mood
- `GET /api/user/mood-history` - View mood trends

## 🧪 Testing

```bash
# Backend tests
cd backend-flask
pytest tests/ -v --cov=backend

# Node.js tests
cd node-services/realtime
npm test

# Frontend E2E tests
cd frontend
npm run test:e2e
```

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Safety Policy](docs/safety_policy.md)
- [Privacy Policy](docs/privacy_policy.md)
- [Clinician Protocol](docs/clinician_protocol.md)
- [Deployment Playbook](docs/deployment_playbook.md)

## ⚠️ Disclaimer

**This is educational software for demonstration purposes.**

This platform is NOT a substitute for professional mental health care. It is designed as a supplementary tool and should be used under the supervision of licensed mental health professionals.

**Crisis Resources:**
- US: National Suicide Prevention Lifeline: 988
- International: https://findahelpline.com/

If you are in crisis, please contact emergency services or a crisis hotline immediately.

## 🔒 Security & Compliance

- All sensitive data is encrypted at rest and in transit
- JWT-based authentication
- Content moderation for harmful content
- Crisis detection with automatic escalation
- GDPR-compliant data export functionality
- Regular security audits recommended

**Note:** For production deployment handling real patient data, ensure compliance with:
- HIPAA (US)
- GDPR (EU)
- Local healthcare data regulations
- Obtain legal review and clinical oversight

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mental health resources from NAMI, SAMHSA, and WHO
- Evidence-based CBT/DBT techniques
- Open-source AI models and frameworks

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Contact: support@example.com

---

**Built with ❤️ for mental health awareness and support**
