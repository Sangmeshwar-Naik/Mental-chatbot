import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { chat } from '../services/api';
import socketService from '../services/socket';
import '../styles/base.css';
import '../styles/chat.css';

function Chat({ user, onLogout }) {
    const [conversations, setConversations] = useState([]);
    const [activeConversation, setActiveConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadConversations();

        // Connect to Socket.IO
        const token = localStorage.getItem('access_token');
        if (token) {
            socketService.connect(token);

            // Listen for new messages
            socketService.on('new_message', handleNewMessage);
        }

        return () => {
            socketService.disconnect();
        };
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadConversations = async () => {
        try {
            setIsLoading(true);
            const response = await chat.getConversations();
            setConversations(response.data.conversations || []);
        } catch (error) {
            console.error('Error loading conversations:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadConversation = async (conversationId) => {
        try {
            const response = await chat.getConversation(conversationId);
            setActiveConversation(response.data.conversation);
            setMessages(response.data.messages || []);
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    };

    const handleNewMessage = (data) => {
        // Handle real-time message updates
        console.log('New message:', data);
    };

    const sendMessage = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim() || isSending) return;

        setIsSending(true);
        const messageText = inputMessage;
        setInputMessage('');

        try {
            const response = await chat.sendMessage(
                messageText,
                activeConversation?.id
            );

            const { conversation_id, user_message, assistant_message, crisis_detected } = response.data;

            // Update messages
            setMessages(prev => [...prev, user_message, assistant_message]);

            // Update active conversation if new
            if (!activeConversation) {
                setActiveConversation({ id: conversation_id });
                loadConversations(); // Refresh conversation list
            }

            // Show crisis alert if detected
            if (crisis_detected) {
                alert('We noticed you may be experiencing distress. Please consider reaching out to a crisis counselor.');
            }

            // Send via socket for real-time updates
            socketService.sendMessage(conversation_id, messageText);

        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
            setInputMessage(messageText); // Restore message
        } finally {
            setIsSending(false);
        }
    };

    const startNewConversation = () => {
        setActiveConversation(null);
        setMessages([]);
    };

    return (
        <div className="chat-container">
            {/* Sidebar */}
            <div className="chat-sidebar">
                <div className="sidebar-header">
                    <h2>Mental Health Support</h2>
                    <button className="btn btn-sm btn-primary" onClick={startNewConversation}>
                        + New Chat
                    </button>
                </div>

                <div className="sidebar-content">
                    <div className="nav-links">
                        <Link to="/chat" className="nav-link active">💬 Chat</Link>
                        <Link to="/journal" className="nav-link">📔 Journal</Link>
                        {user?.role === 'admin' && (
                            <Link to="/admin" className="nav-link">⚙️ Admin</Link>
                        )}
                    </div>

                    <div className="conversation-list">
                        <h3 style={{ fontSize: '0.875rem', color: 'var(--gray-500)', marginBottom: 'var(--spacing-sm)' }}>
                            Conversations
                        </h3>
                        {conversations.map(conv => (
                            <div
                                key={conv.id}
                                className={`conversation-item ${activeConversation?.id === conv.id ? 'active' : ''}`}
                                onClick={() => loadConversation(conv.id)}
                            >
                                <div className="conversation-title">{conv.title}</div>
                                <div className="conversation-meta">
                                    {conv.message_count} messages
                                    {conv.is_flagged && <span className="flag-badge">⚠️</span>}
                                </div>
                            </div>
                        ))}
                        {conversations.length === 0 && (
                            <p style={{ color: 'var(--gray-400)', fontSize: '0.875rem', textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
                                No conversations yet. Start chatting!
                            </p>
                        )}
                    </div>
                </div>

                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="user-avatar">{user?.username?.charAt(0).toUpperCase()}</div>
                        <div className="user-details">
                            <div className="user-name">{user?.username}</div>
                            <div className="user-email">{user?.email}</div>
                        </div>
                    </div>
                    <button className="btn btn-sm btn-secondary" onClick={onLogout}>
                        Logout
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="chat-main">
                <div className="chat-header">
                    <h3>{activeConversation ? activeConversation.title : 'New Conversation'}</h3>
                    <div className="crisis-info">
                        <span style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                            Crisis? Call 988 (US)
                        </span>
                    </div>
                </div>

                <div className="chat-messages">
                    {messages.length === 0 && !activeConversation && (
                        <div className="welcome-message">
                            <h2>Welcome to Mental Health Support</h2>
                            <p>I'm here to listen and provide compassionate support. How are you feeling today?</p>
                            <div className="quick-actions">
                                <button className="quick-action-btn">😊 Feeling good</button>
                                <button className="quick-action-btn">😐 Feeling okay</button>
                                <button className="quick-action-btn">😔 Feeling down</button>
                                <button className="quick-action-btn">😰 Feeling anxious</button>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div key={msg.id || index} className={`message ${msg.role}`}>
                            <div className="message-avatar">
                                {msg.role === 'user' ? user?.username?.charAt(0).toUpperCase() : '🤖'}
                            </div>
                            <div className="message-content">
                                <div className="message-text">{msg.content}</div>
                                <div className="message-time">
                                    {new Date(msg.created_at).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))}

                    {isSending && (
                        <div className="message assistant">
                            <div className="message-avatar">🤖</div>
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                    <form onSubmit={sendMessage} className="chat-input-form">
                        <textarea
                            className="chat-input"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage(e);
                                }
                            }}
                            placeholder="Type your message... (Press Enter to send)"
                            rows="3"
                            disabled={isSending}
                        />
                        <button
                            type="submit"
                            className="btn btn-primary send-button"
                            disabled={!inputMessage.trim() || isSending}
                        >
                            {isSending ? 'Sending...' : 'Send'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Chat;
