/**
 * Real-time Socket.IO Server for Mental Health Chatbot
 */
require('dotenv').config();
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const jwt = require('jsonwebtoken');
const redis = require('redis');

const app = express();
const server = http.createServer(app);

// Socket.IO configuration
const io = socketIo(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});

// Redis client for pub/sub
const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.connect().catch(console.error);

// JWT authentication middleware for Socket.IO
io.use((socket, next) => {
    const token = socket.handshake.auth.token;

    if (!token) {
        return next(new Error('Authentication required'));
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'jwt-secret-change-me');
        socket.userId = decoded.sub || decoded.identity;
        next();
    } catch (error) {
        next(new Error('Invalid token'));
    }
});

// Store active connections
const activeUsers = new Map();

// Socket.IO event handlers
io.on('connection', (socket) => {
    console.log(`User connected: ${socket.userId}`);

    // Add user to active users
    activeUsers.set(socket.userId, socket.id);

    // Join user's personal room
    socket.join(`user_${socket.userId}`);

    // Emit online status
    io.emit('user_status', {
        userId: socket.userId,
        status: 'online',
        timestamp: new Date().toISOString()
    });

    // Handle typing indicator
    socket.on('typing', (data) => {
        socket.to(`user_${socket.userId}`).emit('typing', {
            userId: socket.userId,
            conversationId: data.conversationId,
            isTyping: data.isTyping
        });
    });

    // Handle message sending (echo for now, backend will persist)
    socket.on('send_message', async (data) => {
        console.log(`Message from user ${socket.userId}:`, data);

        // Broadcast to user's room (for multi-device support)
        io.to(`user_${socket.userId}`).emit('new_message', {
            conversationId: data.conversationId,
            message: data.message,
            timestamp: new Date().toISOString()
        });

        // Store in Redis for temporary message queue
        await redisClient.lPush(
            `messages:${data.conversationId}`,
            JSON.stringify({
                userId: socket.userId,
                message: data.message,
                timestamp: new Date().toISOString()
            })
        );
    });

    // Handle read receipts
    socket.on('message_read', (data) => {
        io.to(`user_${socket.userId}`).emit('message_read', {
            messageId: data.messageId,
            conversationId: data.conversationId,
            readAt: new Date().toISOString()
        });
    });

    // Handle admin alerts (crisis situations)
    socket.on('admin_alert', (data) => {
        // Emit to all admin users
        io.to('admin_room').emit('crisis_alert', {
            userId: socket.userId,
            conversationId: data.conversationId,
            riskLevel: data.riskLevel,
            timestamp: new Date().toISOString()
        });
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.userId}`);
        activeUsers.delete(socket.userId);

        // Emit offline status
        io.emit('user_status', {
            userId: socket.userId,
            status: 'offline',
            timestamp: new Date().toISOString()
        });
    });
});

// HTTP endpoints
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'realtime-socket-server',
        activeConnections: io.engine.clientsCount
    });
});

app.get('/active-users', (req, res) => {
    res.json({
        count: activeUsers.size,
        users: Array.from(activeUsers.keys())
    });
});

// Start server
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
    console.log(`Socket.IO server running on port ${PORT}`);
    console.log(`Active connections: ${io.engine.clientsCount}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, closing server...');
    await redisClient.quit();
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
