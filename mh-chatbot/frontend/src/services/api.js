/**
 * API Service - Axios wrapper for backend API calls
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor  to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
                        headers: { Authorization: `Bearer ${refreshToken}` }
                    });

                    const { access_token } = response.data;
                    localStorage.setItem('access_token', access_token);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, logout
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Auth endpoints
export const auth = {
    login: (email, password) =>
        api.post('/auth/login', { email, password }),

    register: (data) =>
        api.post('/auth/register', data),

    logout: () =>
        api.post('/auth/logout'),

    getCurrentUser: () =>
        api.get('/auth/me')
};

// Chat endpoints
export const chat = {
    sendMessage: (message, conversationId = null) =>
        api.post('/chat/message', { message, conversation_id: conversationId }),

    getConversations: () =>
        api.get('/chat/conversations'),

    getConversation: (conversationId) =>
        api.get(`/chat/conversation/${conversationId}`),

    deleteConversation: (conversationId) =>
        api.delete(`/chat/conversation/${conversationId}`),

    submitFeedback: (messageId, rating, comment = null) =>
        api.post('/chat/feedback', { message_id: messageId, rating, comment })
};

// User endpoints
export const user = {
    getProfile: () =>
        api.get('/user/profile'),

    updateProfile: (data) =>
        api.put('/user/profile', data),

    logMood: (moodData) =>
        api.post('/user/mood', moodData),

    getMoodHistory: (days = 30) =>
        api.get(`/user/mood-history?days=${days}`),

    getDashboard: () =>
        api.get('/user/dashboard')
};

// Screening endpoints
export const screenings = {
    submitPHQ9: (responses) =>
        api.post('/screenings/phq9', { responses }),

    submitGAD7: (responses) =>
        api.post('/screenings/gad7', { responses }),

    getHistory: () =>
        api.get('/screenings/history'),

    getQuestions: (type) =>
        api.get(`/screenings/questions?type=${type}`)
};

// Admin endpoints
export const admin = {
    getDashboard: () =>
        api.get('/admin/dashboard'),

    getFlaggedConversations: () =>
        api.get('/admin/flagged-conversations'),

    getHighRiskUsers: () =>
        api.get('/admin/high-risk-users'),

    getUserConversations: (userId) =>
        api.get(`/admin/user/${userId}/conversations`),

    getConversationMessages: (conversationId) =>
        api.get(`/admin/conversation/${conversationId}/messages`),

    addNote: (userId, note, noteType = 'observation', isCritical = false) =>
        api.post('/admin/note', { user_id: userId, note, note_type: noteType, is_critical: isCritical }),

    getUserNotes: (userId) =>
        api.get(`/admin/user/${userId}/notes`)
};

export default api;
