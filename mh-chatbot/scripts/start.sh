#!/bin/bash
# Quick start script for development

echo "🚀 Starting Mental Health Chatbot services..."

# Check if .env exists
if [ ! -f backend-flask/.env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp backend-flask/.env.example backend-flask/.env
    echo "✅ Please edit backend-flask/.env with your API keys before continuing."
    exit 1
fi

# Start Docker Compose
echo "🐳 Starting Docker containers..."
cd infra
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking service health..."
curl -s http://localhost:5000/health | grep -q "healthy" && echo "✅ Backend: healthy" || echo "❌ Backend: unhealthy"
curl -s http://localhost:3001/health | grep -q "healthy" && echo "✅ Real-time: healthy" || echo "❌ Real-time: unhealthy"

echo ""
echo "🎉 Services are running!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000/api"
echo "   Socket.IO: http://localhost:3001"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
echo "Don't forget to create an admin user:"
echo "docker exec -it mh-backend python ../scripts/create_admin.py"
