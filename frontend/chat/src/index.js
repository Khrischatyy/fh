require('dotenv').config();
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const Redis = require('ioredis');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const { Pool } = require('pg');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
    path: '/socket.io/',
    cors: {
        origin: '*',
        methods: ['GET', 'POST', 'OPTIONS'],
        allowedHeaders: ['Content-Type', 'Authorization'],
        credentials: true
    },
    transports: ['websocket', 'polling'],
    pingTimeout: 60000,
    pingInterval: 25000
});

// Redis connection
const redis = new Redis({
    host: process.env.REDIS_HOST || 'redis',
    port: process.env.REDIS_PORT || 6379
});

// PostgreSQL connection
const pool = new Pool({
    user: process.env.DB_USERNAME,
    host: process.env.DB_HOST,
    database: process.env.DB_DATABASE,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
});

console.log('[chat] Socket.IO server starting, adding middleware...');
io.use(async (socket, next) => {
    console.log('[chat] Auth middleware - called');
    const token = socket.handshake.auth.token;
    console.log('[chat] Auth middleware - received token:', token);

    if (!token) {
        console.log('[chat] Auth middleware - no token provided');
        return next(new Error('No token provided'));
    }

    try {
        console.log('[chat] Auth middleware - requesting /api/v1/user/me ...');
        const response = await axios.get('http://nginx/api/v1/user/me', {
            headers: {
                Authorization: `Bearer ${token}`,
                Accept: 'application/json'
            }
        });
        console.log('[chat] Auth middleware - full API response:', JSON.stringify(response.data));
        const userData = response.data.data;
        const user = userData.user;
        console.log('[chat] Auth middleware - user from API:', user);

        if (!user || !user.id) {
            console.log('[chat] Auth middleware - user or user.id not found in API response');
            return next(new Error('Invalid user'));
        }

        socket.user = { id: user.id, ...user };
        socket.userToken = token;
        console.log('[chat] Auth middleware - authentication successful for user id:', user.id);
        next();
    } catch (err) {
        console.error('[chat] Auth middleware - error:', err?.response?.data || err.message);
        if (err && err.stack) {
            console.error('[chat] Auth middleware - error stack:', err.stack);
        }
        next(new Error('Authentication error'));
    }
});

// Add more logging for connection events
io.engine.on("connection_error", (err) => {
    console.log('[chat] Connection error:', err);
});

io.engine.on("connection", (socket) => {
    console.log('[chat] New connection:', socket.id);
});

// Socket connection handling
io.on('connection', async (socket) => {
    console.log('[chat] io.on(connection) - socket.id:', socket.id);
    console.log('[chat] New connection:', socket.id, 'user:', socket.user);
    
    // Log all events
    socket.onAny((event, ...args) => {
        console.log('[chat] socket.onAny', event, args);
    });

    // Join user's personal room
    socket.join(`user_${socket.user.id}`);
    console.log('[chat] User joined room:', `user_${socket.user.id}`);

    // Handle private messages
    socket.on('private-message', async (data) => {
        const { recipientId, message, addressId } = data;
        const senderId = socket.user.id;
        console.log('[chat] Incoming private-message:', { userId: senderId, data });
        try {
            const apiUrl = 'http://nginx/api/v1/messages';
            const apiData = {
                recipient_id: recipientId,
                address_id: addressId,
                content: message
            };
            const apiHeaders = {
                Accept: 'application/json',
                Authorization: `Bearer ${socket.userToken}`
            };
            console.log('[chat] Sending message to API:', { url: apiUrl, data: apiData, headers: apiHeaders });
            const response = await axios.post(
                apiUrl,
                apiData,
                { headers: apiHeaders }
            );
            console.log('[chat] API response:', response.data);
            const savedMessage = response.data.data;
            const messageData = {
                id: savedMessage.id,
                senderId,
                recipientId,
                addressId,
                message: savedMessage.content,
                createdAt: savedMessage.created_at
            };
            io.to(`user_${recipientId}`).emit('new-message', messageData);
            io.to(`user_${senderId}`).emit('new-message', messageData);
        } catch (error) {
            console.error('[chat] Error saving message via API:', error?.response?.data || error.message);
            socket.emit('error', 'Failed to send message');
        }
    });

    // Handle message history request
    socket.on('get-message-history', async (data) => {
        const { addressId, recipientId } = data;
        try {
            const apiUrl = 'http://nginx/api/v1/messages/history';
            const apiHeaders = {
                Accept: 'application/json',
                Authorization: `Bearer ${socket.userToken}`
            };
            const apiData = {
                recipient_id: recipientId,
                address_id: addressId
            };
            console.log('[chat] Fetching message history from API:', { url: apiUrl, data: apiData, headers: apiHeaders });
            const response = await axios.post(
                apiUrl,
                apiData,
                { headers: apiHeaders }
            );
            console.log('[chat] Message history API response:', response.data);
            socket.emit('message-history', response.data.data);
        } catch (error) {
            console.error('[chat] Error fetching message history via API:', error?.response?.data || error.message);
            socket.emit('error', 'Failed to fetch message history');
        }
    });

    socket.on('disconnect', () => {
        console.log(`[chat] User disconnected: ${socket.user.id}`);
    });
});

// Redis subscription for message broadcasting
redis.subscribe('private-chat', () => {
    console.log('Subscribed to Redis channel: private-chat');
});

redis.on('message', (channel, message) => {
    const parsedMessage = JSON.parse(message);
    io.to(`user_${parsedMessage.recipientId}`).emit('new-message', parsedMessage);
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

const PORT = process.env.PORT || 6001;
server.listen(PORT, () => {
    console.log(`Chat service is running on port ${PORT}`);
}); 