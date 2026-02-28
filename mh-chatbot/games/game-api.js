/**
 * Game Backend Integration
 * Common functions for saving game scores to backend
 */

const GameAPI = {
    /**
     * Save game score to backend
     * @param {string} gameName - Name of the game
     * @param {number} score - Score achieved
     * @param {object} additionalData - Extra data to save (optional)
     */
    async saveScore(gameName, score, additionalData = {}) {
        try {
            const response = await fetch('/api/games/save-score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game: gameName,
                    score: score,
                    data: additionalData
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log(`✅ Score saved for ${gameName}: ${score}`);
                return true;
            } else {
                console.warn('⚠️ Failed to save score:', data.error);
                return false;
            }
        } catch (error) {
            console.error('❌ Error saving score:', error);
            return false;
        }
    },

    /**
     * Get user's scores for a specific game
     * @param {string} gameName - Name of the game
     */
    async getScores(gameName) {
        try {
            const response = await fetch(`/api/games/get-scores/${gameName}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('❌ Error fetching scores:', error);
            return { scores: [], best: 0, total_plays: 0 };
        }
    },

    /**
     * Get leaderboard for a game
     * @param {string} gameName - Name of the game
     */
    async getLeaderboard(gameName) {
        try {
            const response = await fetch(`/api/games/leaderboard/${gameName}`);
            const data = await response.json();
            return data.leaderboard || [];
        } catch (error) {
            console.error('❌ Error fetching leaderboard:', error);
            return [];
        }
    },

    /**
     * Get overall user gaming stats
     */
    async getUserStats() {
        try {
            const response = await fetch('/api/games/stats');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('❌ Error fetching user stats:', error);
            return { total_games_played: 0, games: {} };
        }
    }
};

// Make available globally
if (typeof window !== 'undefined') {
    window.GameAPI = GameAPI;
}
