"""
Game Progress Tracking API
Endpoints for saving and retrieving game scores
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

games_api = Blueprint('games_api', __name__)

# In-memory storage (replace with database in production)
game_scores = {}

@games_api.route('/api/games/save-score', methods=['POST'])
@login_required
def save_score():
    """Save a game score for the current user"""
    try:
        data = request.json
        game_name = data.get('game')
        score = data.get('score')
        additional_data = data.get('data', {})
        
        if not game_name or score is None:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_id = current_user.id
        
        if user_id not in game_scores:
            game_scores[user_id] = {}
        
        if game_name not in game_scores[user_id]:
            game_scores[user_id][game_name] = []
        
        score_entry = {
            'score': score,
            'timestamp': datetime.now().isoformat(),
            'data': additional_data
        }
        
        game_scores[user_id][game_name].append(score_entry)
        
        # Keep only last 50 scores per game
        game_scores[user_id][game_name] = game_scores[user_id][game_name][-50:]
        
        return jsonify({
            'success': True,
            'message': 'Score saved successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_api.route('/api/games/get-scores/<game_name>', methods=['GET'])
@login_required
def get_scores(game_name):
    """Get all scores for a specific game"""
    try:
        user_id = current_user.id
        
        if user_id not in game_scores or game_name not in game_scores[user_id]:
            return jsonify({
                'scores': [],
                'best': 0,
                'total_plays': 0
            })
        
        scores = game_scores[user_id][game_name]
        score_values = [s['score'] for s in scores]
        
        return jsonify({
            'scores': scores,
            'best': max(score_values) if score_values else 0,
            'total_plays': len(scores),
            'average': sum(score_values) / len(score_values) if score_values else 0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_api.route('/api/games/leaderboard/<game_name>', methods=['GET'])
def get_leaderboard(game_name):
    """Get top scores for a game across all users"""
    try:
        all_scores = []
        
        for user_id, games in game_scores.items():
            if game_name in games:
                user_best = max([s['score'] for s in games[game_name]])
                all_scores.append({
                    'user_id': user_id,
                    'score': user_best
                })
        
        # Sort by score descending
        all_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'leaderboard': all_scores[:10]  # Top 10
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_api.route('/api/games/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get overall gaming statistics for current user"""
    try:
        user_id = current_user.id
        
        if user_id not in game_scores:
            return jsonify({
                'total_games_played': 0,
                'games': {}
            })
        
        stats = {
            'total_games_played': sum(len(scores) for scores in game_scores[user_id].values()),
            'games': {}
        }
        
        for game_name, scores in game_scores[user_id].items():
            score_values = [s['score'] for s in scores]
            stats['games'][game_name] = {
                'plays': len(scores),
                'best': max(score_values) if score_values else 0,
                'average': sum(score_values) / len(score_values) if score_values else 0,
                'last_played': scores[-1]['timestamp'] if scores else None
            }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
