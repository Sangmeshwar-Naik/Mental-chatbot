# Game Progress Tracking Integration Guide

## Setup Instructions

The backend API for game score tracking is now integrated!

### What's Been Done:

1. ✅ Created `backend-flask/games_api.py` - Flask API endpoints
2. ✅ Created `games/game-api.js` - JavaScript client library  
3. ✅ Integrated API into `final_working_chat.py`

### How to Use:

#### 1. Add Script to Games

Add this line before `</body>` in each game HTML file:

```html
<script src="../games/game-api.js"></script>
```

#### 2. Save Scores

Add this code when the game ends:

**Reaction Time Example:**
```javascript
// After showResults()
await GameAPI.saveScore('reaction-time', averageTime, {
    rounds: scores.length,
    best: Math.min(...scores)
});
```

**Memory Match Example:**
```javascript
// In showVictory()
await GameAPI.saveScore('memory-match', score, {
    difficulty: gridSize,
    moves: moves,
    time: seconds,
    stars: stars
});
```

**Bubble Shooter Example:**
```javascript
// When level complete
await GameAPI.saveScore('bubble-shooter', score, {
    level: level,
    combos: maxCombo
});
```

**Block Blast Example:**
```javascript
// When game over
await GameAPI.saveScore('block-blast', score, {
    lines_cleared: totalLines
});
```

### API Endpoints Available:

1. **Save Score**: `POST /api/games/save-score`
2. **Get Scores**: `GET /api/games/get-scores/<game>`
3. **Leaderboard**: `GET /api/games/leaderboard/<game>`
4. **User Stats**: `GET /api/games/stats`

### Testing:

1. Start the Flask server
2. Open a game
3. Complete a game session
4. Check console for "✅ Score saved..." message
5. Visit `/api/games/stats` to see all your scores

### Optional - Display Stats:

Add to games.html:

```html
<script src="games/game-api.js"></script>
<script>
async function loadStats() {
    const stats = await GameAPI.getUserStats();
    console.log('Total games played:', stats.total_games_played);
    // Display in UI as desired
}
loadStats();
</script>
```

### Note:

Currently using in-memory storage. For production, replace with database:
- Add GameScore model to database
- Update games_api.py to use SQLAlchemy
- Migrate data persistence logic
