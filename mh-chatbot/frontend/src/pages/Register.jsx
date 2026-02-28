import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { auth } from '../services/api';
import '../styles/base.css';

function Register({ onRegister }) {
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        age: '',
        agreeToTerms: false
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // Client-side validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setIsLoading(false);
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            setIsLoading(false);
            return;
        }

        if (!formData.agreeToTerms) {
            setError('You must agree to the terms and conditions');
            setIsLoading(false);
            return;
        }

        try {
            const { confirmPassword, agreeToTerms, ...registerData } = formData;
            const response = await auth.register(registerData);
            const { access_token, refresh_token, user } = response.data;

            // Store tokens
            localStorage.setItem('refresh_token', refresh_token);

            // Call parent register handler
            onRegister(access_token, user);
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center" style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '20px' }}>
            <div className="card" style={{ width: '100%', maxWidth: '500px' }}>
                <div className="text-center mb-lg">
                    <h1 className="text-primary">Create Account</h1>
                    <p className="text-gray">Join our supportive community</p>
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
                    <div className="flex gap-md">
                        <div style={{ flex: 1 }}>
                            <label htmlFor="first_name" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                                First Name
                            </label>
                            <input
                                type="text"
                                id="first_name"
                                name="first_name"
                                className="input"
                                value={formData.first_name}
                                onChange={handleChange}
                                disabled={isLoading}
                            />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label htmlFor="last_name" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                                Last Name
                            </label>
                            <input
                                type="text"
                                id="last_name"
                                name="last_name"
                                className="input"
                                value={formData.last_name}
                                onChange={handleChange}
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    <div>
                        <label htmlFor="email" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Email Address *
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
                        <label htmlFor="username" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Username *
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            className="input"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            disabled={isLoading}
                            placeholder="Choose a username"
                        />
                    </div>

                    <div>
                        <label htmlFor="age" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Age
                        </label>
                        <input
                            type="number"
                            id="age"
                            name="age"
                            className="input"
                            value={formData.age}
                            onChange={handleChange}
                            disabled={isLoading}
                            min="13"
                            max="120"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Password *
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
                            placeholder="Min. 8 characters"
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="font-medium" style={{ display: 'block', marginBottom: 'var(--spacing-sm)' }}>
                            Confirm Password *
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            className="input"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            disabled={isLoading}
                            placeholder="Re-enter password"
                        />
                    </div>

                    <div className="flex items-center gap-sm">
                        <input
                            type="checkbox"
                            id="agreeToTerms"
                            name="agreeToTerms"
                            checked={formData.agreeToTerms}
                            onChange={handleChange}
                            disabled={isLoading}
                        />
                        <label htmlFor="agreeToTerms" style={{ fontSize: '0.875rem' }}>
                            I agree to the Terms of Service and Privacy Policy
                        </label>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <div className="text-center mt-lg">
                    <p className="text-gray">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary font-semibold">
                            Sign in here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Register;
