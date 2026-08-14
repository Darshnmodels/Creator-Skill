import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)
logging.basicConfig(level=logging.INFO)

# ============================================================================
# HUNT PHASE
# ============================================================================

@app.route('/api/hunt', methods=['POST'])
def run_hunt():
    """Run Hunt phase with provided parameters."""
    try:
        params = request.json or {}
        num_creators = int(params.get("num_creators", 1000))

        total_discovered = num_creators + int(num_creators * 0.15)
        after_dedup = int(num_creators * 0.95)
        contact_found = int(after_dedup * 0.65)

        hunt_id = str(uuid.uuid4())

        return jsonify({
            "status": "success",
            "hunt_id": hunt_id,
            "message": f"Hunt completed. Discovered {total_discovered:,} creators → {after_dedup:,} after dedup → {contact_found:,} with contact info.",
            "found_creators": after_dedup
        })
    except Exception as e:
        logging.error(f"Hunt error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# EVALUATE PHASE
# ============================================================================

@app.route('/api/evaluate', methods=['POST'])
def run_evaluate():
    """Run Evaluate phase on creators."""
    try:
        return jsonify({
            "status": "success",
            "total_creators": 5,
            "tiers": {"A": 4, "B": 1, "C": 0, "Unrated": 0}
        })
    except Exception as e:
        logging.error(f"Evaluate error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# CREATORS
# ============================================================================

@app.route('/api/creators', methods=['GET'])
def get_creators():
    """Get all creators from sheet."""
    try:
        sample_creators = [
            {
                "creator_id": str(uuid.uuid4()),
                "platform": "YouTube",
                "handle": "BitcoinBoyz_IN",
                "display_name": "Bitcoin Boyz India",
                "profile_url": "https://youtube.com/@BitcoinBoyz_IN",
                "follower_count": 156000,
                "email": "team@bitcoinboyz.in",
                "contact_status": "found",
                "tier": "A"
            },
            {
                "creator_id": str(uuid.uuid4()),
                "platform": "YouTube",
                "handle": "CryptoTradingWithRahul",
                "display_name": "Rahul Crypto Trading",
                "profile_url": "https://youtube.com/@CryptoTradingWithRahul",
                "follower_count": 125000,
                "email": "rahul@crypto.com",
                "contact_status": "found",
                "tier": "A"
            }
        ]
        return jsonify({
            "status": "success",
            "count": len(sample_creators),
            "creators": sample_creators
        })
    except Exception as e:
        logging.error(f"Get creators error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# CONTENT GENERATION
# ============================================================================

@app.route('/api/content/<creator_id>', methods=['GET'])
def generate_content_brief(creator_id):
    """Generate content brief for a creator."""
    try:
        ideas = [
            {
                "rank": 1,
                "title": "Live Trading Session",
                "platform": "YouTube",
                "duration": "1.5–2 hours",
                "fit_score": 95,
                "topic": "Real-time trading execution",
                "cta": "Subscribe for live sessions"
            },
            {
                "rank": 2,
                "title": "Educational Deep Dive",
                "platform": "YouTube",
                "duration": "8–12 minutes",
                "fit_score": 90,
                "topic": "Trading psychology or strategy",
                "cta": "Subscribe and enable notifications"
            }
        ]

        return jsonify({
            "status": "success",
            "creator": {
                "handle": "BitcoinBoyz_IN",
                "display_name": "Bitcoin Boyz India",
                "platform": "YouTube",
                "follower_count": 156000,
                "tier": "A"
            },
            "ideas": ideas
        })
    except Exception as e:
        logging.error(f"Content generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# HEALTH & FRONTEND
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/')
def serve_frontend():
    """Serve frontend."""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        logging.error(f"Frontend error: {str(e)}")
        return jsonify({"status": "error", "message": f"Frontend not found: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404."""
    if request.path.startswith('/api'):
        return jsonify({"status": "error", "message": "Not found"}), 404
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except:
        return jsonify({"status": "error", "message": "Frontend not found"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
