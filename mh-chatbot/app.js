// ========================================
// Main Application JavaScript
// ========================================

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    console.log('🌸 Mental Health Companion - Initializing...');

    // Load user stats
    loadUserStats();

    // Set up navigation
    setupNavigation();

    // Set up profile
    setupProfile();

    // Set up feature cards
    setupFeatureCards();

    // Update streak
    Storage.updateStreak();

    console.log('✅ Application initialized successfully');
}

// Load and display user stats
function loadUserStats() {
    const stats = Storage.load(Storage.KEYS.STATS);

    // Update streak display
    const streakElement = document.getElementById('streak-days');
    if (streakElement) {
        streakElement.textContent = stats.streakDays || 0;
    }

    // Update activities display
    const activitiesElement = document.getElementById('activities-completed');
    if (activitiesElement) {
        activitiesElement.textContent = stats.activitiesCompleted || 0;
    }

    // Update profile stats
    const totalActivitiesElement = document.getElementById('total-activities');
    if (totalActivitiesElement) {
        totalActivitiesElement.textContent = stats.activitiesCompleted || 0;
    }

    const journalCountElement = document.getElementById('journal-count');
    if (journalCountElement) {
        journalCountElement.textContent = stats.journalCount || 0;
    }

    const daysActiveElement = document.getElementById('days-active');
    if (daysActiveElement) {
        const createdDate = new Date(Storage.load(Storage.KEYS.USER_PROFILE).createdAt);
        const today = new Date();
        const daysDiff = Math.floor((today - createdDate) / (1000 * 60 * 60 * 24));
        daysActiveElement.textContent = daysDiff || 1;
    }
}

// Setup navigation between sections
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.content-section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetSection = button.getAttribute('data-section');

            // Remove active class from all buttons and sections
            navButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button and target section
            button.classList.add('active');
            const targetElement = document.getElementById(`${targetSection}-section`);
            if (targetElement) {
                targetElement.classList.add('active');
            }
        });
    });
}

// Setup profile functionality
function setupProfile() {
    const profile = Storage.load(Storage.KEYS.USER_PROFILE);

    // Load profile data
    const displayNameInput = document.getElementById('display-name');
    const emailInput = document.getElementById('email');

    if (displayNameInput && profile.displayName) {
        displayNameInput.value = profile.displayName;
    }

    if (emailInput && profile.email) {
        emailInput.value = profile.email;
    }

    // Save on input change
    if (displayNameInput) {
        displayNameInput.addEventListener('blur', () => {
            profile.displayName = displayNameInput.value;
            Storage.save(Storage.KEYS.USER_PROFILE, profile);
        });
    }

    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            profile.email = emailInput.value;
            Storage.save(Storage.KEYS.USER_PROFILE, profile);
        });
    }

    // Export data button
    const exportBtn = document.getElementById('export-data');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportUserData);
    }

    // Import data button
    const importBtn = document.getElementById('import-data');
    if (importBtn) {
        importBtn.addEventListener('click', importUserData);
    }

    // Clear data button
    const clearBtn = document.getElementById('clear-data');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllData);
    }
}

// Setup feature card navigation
function setupFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards.forEach(card => {
        card.addEventListener('click', () => {
            const feature = card.getAttribute('data-feature');
            openFeature(feature);
        });
    });
}

// Open a specific feature
function openFeature(featureName) {
    console.log(`Opening feature: ${featureName}`);

    // Increment activity count
    Storage.incrementActivity();
    loadUserStats();

    // Feature routes
    const featureRoutes = {
        'coping-plan': 'features/coping-plan.html',
        'therapy-exercises': 'features/therapy-exercises.html',
        'journal': 'features/journal.html',
        'habit-tracker': 'features/habit-tracker.html',
        'voice-chat': 'features/voice-chat.html',
        'breathing': 'features/breathing.html',
        'focus-timer': 'features/focus-timer.html',
        'grounding': 'features/grounding.html',
        'meditation': 'features/meditation.html',
        'chess': 'games/chess.html',
        'memory-cards': 'games/memory-cards.html',
        'bubble-shooter': 'games/bubble-shooter.html',
        'block-blast': 'games/block-blast.html',
        'reaction-game': 'games/reaction-game.html',
        'color-therapy': 'games/color-therapy.html',
        'kindness-challenge': 'games/kindness-challenge.html',
        'mood-matching': 'games/mood-matching.html',
        'empathy-quiz': 'games/empathy-quiz.html',
        'wellness-bingo': 'games/wellness-bingo.html',
        'clinician-dashboard': 'features/clinician-dashboard.html'
    };

    const route = featureRoutes[featureName];
    if (route) {
        // Navigate to the feature page
        window.location.href = route;
    } else {
        showNotification('Feature not found', 'error');
    }
}

// Show coming soon modal (temporary until features are built)
function showFeatureComingSoon(featureName) {
    const featureNames = {
        'coping-plan': 'Personalized Coping Plan Generator',
        'therapy-exercises': 'Therapy Exercises',
        'journal': 'AI Journal Assistant',
        'habit-tracker': 'Habit Tracker',
        'voice-chat': 'Voice Conversation',
        'breathing': 'Breathing Exercises',
        'focus-timer': 'Focus Timer',
        'grounding': 'Grounding Exercise',
        'meditation': 'Guided Meditation',
        'chess': 'Chess Game',
        'memory-cards': 'Memory Match Game',
        'bubble-shooter': 'Bubble Shooter',
        'block-blast': 'Block Blast Puzzle',
        'reaction-game': 'Reaction Time Game',
        'color-therapy': 'Color Therapy',
        'kindness-challenge': 'Kindness Challenge',
        'mood-matching': 'Mood Matching Game',
        'empathy-quiz': 'Empathy Quiz',
        'wellness-bingo': 'Wellness Bingo',
        'clinician-dashboard': 'Clinician Dashboard'
    };

    showNotification(`${featureNames[featureName]} - Coming Soon! 🎉`, 'info');
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#667eea'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export user data
function exportUserData() {
    const data = Storage.exportData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `mental-health-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification('Data exported successfully! 📥', 'success');
}

// Import user data
function importUserData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const success = Storage.importData(event.target.result);
                if (success) {
                    showNotification('Data imported successfully! 📤', 'success');
                    loadUserStats();
                    setupProfile();
                } else {
                    showNotification('Failed to import data', 'error');
                }
            } catch (error) {
                showNotification('Invalid data file', 'error');
            }
        };
        reader.readAsText(file);
    });

    input.click();
}

// Clear all data
function clearAllData() {
    if (confirm('Are you sure you want to delete all your data? This cannot be undone.')) {
        if (confirm('This will permanently delete all journals, habits, and progress. Continue?')) {
            Storage.clearAll();
            Storage.initialize();
            showNotification('All data cleared', 'success');
            loadUserStats();
            setupProfile();
        }
    }
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility: Get greeting based on time
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
}
