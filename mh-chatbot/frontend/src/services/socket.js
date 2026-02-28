/**
 * Socket.IO Client Service
 */
import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:3001';

class SocketService {
    constructor() {
        this.socket = null;
        this.listeners = new Map();
    }

    connect(token) {
        if (this.socket?.connected) {
            return;
        }

        this.socket = io(SOCKET_URL, {
            auth: {
                token: token
            },
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        });

        this.socket.on('connect', () => {
            console.log('Socket connected:', this.socket.id);
        });

        this.socket.on('disconnect', () => {
            console.log('Socket disconnected');
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.listeners.clear();
        }
    }

    // Send typing indicator
    sendTyping(conversationId, isTyping) {
        if (this.socket) {
            this.socket.emit('typing', { conversationId, isTyping });
        }
    }

    // Send message
    sendMessage(conversationId, message) {
        if (this.socket) {
            this.socket.emit('send_message', { conversationId, message });
        }
    }

    // Mark message as read
    markAsRead(conversationId, messageId) {
        if (this.socket) {
            this.socket.emit('message_read', { conversationId, messageId });
        }
    }

    // Listen for events
    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);

            // Store listener for cleanup
            if (!this.listeners.has(event)) {
                this.listeners.set(event, []);
            }
            this.listeners.get(event).push(callback);
        }
    }

    // Remove event listener
    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback);

            // Remove from stored listeners
            if (this.listeners.has(event)) {
                const callbacks = this.listeners.get(event);
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        }
    }

    // Remove all listeners for an event
    removeAllListeners(event) {
        if (this.socket) {
            this.socket.removeAllListeners(event);
            this.listeners.delete(event);
        }
    }
}

// Export singleton instance
const socketService = new SocketService();
export default socketService;
