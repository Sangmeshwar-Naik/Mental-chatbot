import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { auth } from '../services/api';
import '../styles/base.css';

function Login({ onLogin }) {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await auth.login(formData.email, formData.password);
            const { access_token, refresh_token, user } = response.data;

            // Store tokens
            localStorage.setItem('refresh_token', refresh_token);

            // Call parent login handler
            onLogin(access_token, user);
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center" style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px', margin: '20px' }}>
                <div className="text-center mb-lg">
                    <h1 className="text-primary">Mental Health Support</h1>
                    <p className="text-gray">AI-powered compassionate care</p>
                </div>

                {error && (
                    <div style={{
                        backgroundColor: '#FEE2E2',
                        color: '#DC2626',
                        padding: 'var(--spacing-md)',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: 'var(--spacing-md)'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-md">
                    <div>
                        <label htmlFor="email" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            className="input"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            disabled={isLoading}
                            placeholder="your@email.com"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            className="input"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            disabled={isLoading}
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div className="text-center mt-lg">
                    <p className="text-gray">
                        Don't have an account?{' '}
                        <Link to="/register" className="text-primary font-semibold">
                            Register here
                        </Link>
                    </p>
                </div>

                <div className="mt-lg" style={{
                    borderTop: '1px solid var(--gray-200)',
                    paddingTop: 'var(--spacing-lg)',
                    fontSize: '0.875rem',
                    color: 'var(--gray-500)',
                    textAlign: 'center'
                }}>
                    <p><strong>Crisis Resources:</strong></p>
                    <p>US: 988 (Suicide & Crisis Lifeline)</p>
                    <p>International: +1-800-273-8255</p>
                </div>
            </div>
        </div>
    );
}

export default Login;
