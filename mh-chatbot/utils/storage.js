// ========================================
// Storage Utilities - LocalStorage Manager
// ========================================

const Storage = {
    // Storage Keys
    KEYS: {
        USER_PROFILE: 'mh_user_profile',
        JOURNAL_ENTRIES: 'mh_journal_entries',
        HABITS: 'mh_habits',
        MOOD_HISTORY: 'mh_mood_history',
        COPING_PLANS: 'mh_coping_plans',
        ACTIVITIES_COMPLETED: 'mh_activities_completed',
        USER_PREFERENCES: 'mh_user_preferences',
        SEMANTIC_MEMORY: 'mh_semantic_memory',
        STATS: 'mh_stats'
    },

    // Save data to localStorage
    save(key, data) {
        try {
            const jsonData = JSON.stringify(data);
            localStorage.setItem(key, jsonData);
            return true;
        } catch (error) {
            console.error('Storage save error:', error);
            return false;
        }
    },

    // Load data from localStorage
    load(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Storage load error:', error);
            return defaultValue;
        }
    },

    // Delete specific key
    delete(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage delete error:', error);
            return false;
        }
    },

    // Clear all app data
    clearAll() {
        try {
            Object.values(this.KEYS).forEach(key => {
                localStorage.removeItem(key);
            });
            return true;
        } catch (error) {
            console.error('Storage clear error:', error);
            return false;
        }
    },

    // Export all user data as JSON
    exportData() {
        const exportData = {};
        Object.entries(this.KEYS).forEach(([name, key]) => {
            const data = this.load(key);
            if (data) {
                exportData[name] = data;
            }
        });
        return JSON.stringify(exportData, null, 2);
    },

    // Import data from JSON
    importData(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            Object.entries(data).forEach(([name, value]) => {
                const key = this.KEYS[name];
                if (key) {
                    this.save(key, value);
                }
            });
            return true;
        } catch (error) {
            console.error('Import error:', error);
            return false;
        }
    },

    // Initialize default data structures
    initialize() {
        // User Profile
        if (!this.load(this.KEYS.USER_PROFILE)) {
            this.save(this.KEYS.USER_PROFILE, {
                displayName: '',
                email: '',
                createdAt: new Date().toISOString()
            });
        }

        // Stats
        if (!this.load(this.KEYS.STATS)) {
            this.save(this.KEYS.STATS, {
                streakDays: 0,
                activitiesCompleted: 0,
                journalCount: 0,
                daysActive: 0,
                lastActiveDate: new Date().toISOString()
            });
        }

        // Journal Entries
        if (!this.load(this.KEYS.JOURNAL_ENTRIES)) {
            this.save(this.KEYS.JOURNAL_ENTRIES, []);
        }

        // Habits
        if (!this.load(this.KEYS.HABITS)) {
            this.save(this.KEYS.HABITS, {
                sleep: [],
                water: [],
                exercise: [],
                diet: [],
                screenTime: []
            });
        }

        // Mood History
        if (!this.load(this.KEYS.MOOD_HISTORY)) {
            this.save(this.KEYS.MOOD_HISTORY, []);
        }

        // User Preferences
        if (!this.load(this.KEYS.USER_PREFERENCES)) {
            this.save(this.KEYS.USER_PREFERENCES, {
                theme: 'default',
                notifications: true,
                voiceEnabled: false
            });
        }

        // Semantic Memory
        if (!this.load(this.KEYS.SEMANTIC_MEMORY)) {
            this.save(this.KEYS.SEMANTIC_MEMORY, {
                goals: [],
                triggers: [],
                successfulCopingTools: [],
                interests: [],
                preferences: {}
            });
        }
    },

    // Update user stats
    updateStats(updates) {
        const stats = this.load(this.KEYS.STATS);
        const newStats = { ...stats, ...updates };
        this.save(this.KEYS.STATS, newStats);
        return newStats;
    },

    // Increment activity count
    incrementActivity() {
        const stats = this.load(this.KEYS.STATS);
        stats.activitiesCompleted += 1;
        this.save(this.KEYS.STATS, stats);
        return stats.activitiesCompleted;
    },

    // Update streak
    updateStreak() {
        const stats = this.load(this.KEYS.STATS);
        const today = new Date().toDateString();
        const lastActive = new Date(stats.lastActiveDate).toDateString();

        if (today !== lastActive) {
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            const yesterdayStr = yesterday.toDateString();

            if (lastActive === yesterdayStr) {
                stats.streakDays += 1;
            } else {
                stats.streakDays = 1;
            }

            stats.lastActiveDate = new Date().toISOString();
            this.save(this.KEYS.STATS, stats);
        }

        return stats.streakDays;
    },

    // Add journal entry
    addJournalEntry(entry) {
        const entries = this.load(this.KEYS.JOURNAL_ENTRIES);
        entries.push({
            id: Date.now(),
            timestamp: new Date().toISOString(),
            ...entry
        });
        this.save(this.KEYS.JOURNAL_ENTRIES, entries);

        // Update journal count
        const stats = this.load(this.KEYS.STATS);
        stats.journalCount = entries.length;
        this.save(this.KEYS.STATS, stats);

        return entries;
    },

    // Get recent journal entries
    getRecentJournals(count = 10) {
        const entries = this.load(this.KEYS.JOURNAL_ENTRIES);
        return entries.slice(-count).reverse();
    },

    // Add mood entry
    addMoodEntry(mood, note = '') {
        const moods = this.load(this.KEYS.MOOD_HISTORY);
        moods.push({
            id: Date.now(),
            timestamp: new Date().toISOString(),
            mood,
            note
        });
        this.save(this.KEYS.MOOD_HISTORY, moods);
        return moods;
    },

    // Get mood history for date range
    getMoodHistory(days = 7) {
        const moods = this.load(this.KEYS.MOOD_HISTORY);
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);

        return moods.filter(entry =>
            new Date(entry.timestamp) >= cutoffDate
        );
    }
};

// Initialize storage on load
Storage.initialize();
