import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Journal from './pages/Journal';
import AdminDashboard from './pages/AdminDashboard';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Check for existing auth token
        const token = localStorage.getItem('access_token');
        if (token) {
            setIsAuthenticated(true);
            // Fetch user data
            fetchUserData(token);
        }
    }, []);

    const fetchUserData = async (token) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
            } else {
                // Token expired or invalid
                handleLogout();
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

    const handleLogin = (token, userData) => {
        localStorage.setItem('access_token', token);
        setIsAuthenticated(true);
        setUser(userData);
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
    };

    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route
                        path="/login"
                        element={
                            isAuthenticated ?
                                <Navigate to="/chat" /> :
                                <Login onLogin={handleLogin} />
                        }
                    />
                    <Route
                        path="/register"
                        element={
                            isAuthenticated ?
                                <Navigate to="/chat" /> :
                                <Register onRegister={handleLogin} />
                        }
                    />
                    <Route
                        path="/chat"
                        element={
                            isAuthenticated ?
                                <Chat user={user} onLogout={handleLogout} /> :
                                <Navigate to="/login" />
                        }
                    />
                    <Route
                        path="/journal"
                        element={
                            isAuthenticated ?
                                <Journal user={user} onLogout={handleLogout} /> :
                                <Navigate to="/login" />
                        }
                    />
                    <Route
                        path="/admin"
                        element={
                            isAuthenticated && user?.role === 'admin' ?
                                <AdminDashboard user={user} onLogout={handleLogout} /> :
                                <Navigate to="/chat" />
                        }
                    />
                    <Route path="/" element={<Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
