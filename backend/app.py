import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)
logging.basicConfig(level=logging.INFO)

# Google Sheets API setup
SHEET_ID = "1zc4XB4aVutf8JubEf_vQrSvpzdr7lTfG2G_sVYEJKwk"
SERVICE_ACCOUNT_KEY = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')

def get_sheets_service():
    """Get authenticated Google Sheets service."""
    if not SERVICE_ACCOUNT_KEY:
        raise Exception("GOOGLE_SERVICE_ACCOUNT_KEY not set")

    service_account_info = json.loads(SERVICE_ACCOUNT_KEY)
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)

# ============================================================================
# HUNT PHASE
# ============================================================================

@app.route('/api/hunt', methods=['POST'])
def run_hunt():
    """Run Hunt phase with provided parameters."""
    try:
        params = request.json

        hunt_id = str(uuid.uuid4())
        hunt_run = {
            "hunt_id": hunt_id,
            "run_date": datetime.now().strftime("%Y-%m-%d"),
            "vertical": params.get("vertical", ""),
            "platforms": params.get("platforms", ""),
            "geography_languages": params.get("geography", ""),
            "follower_min_max": f"{params.get('follower_min', 10000)}-{params.get('follower_max', 999999)}",
            "keywords_used": params.get("keywords_count", 0),
            "total_discovered": params.get("total_discovered", 0),
            "after_dedup": params.get("after_dedup", 0),
            "contact_found_count": params.get("contact_found", 0),
            "creators_added_to_db": params.get("added", 0)
        }

        return jsonify({
            "status": "success",
            "hunt_id": hunt_id,
            "message": f"Hunt completed. {hunt_run['after_dedup']} creators discovered.",
            "hunt_run": hunt_run
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# EVALUATE PHASE
# ============================================================================

@app.route('/api/evaluate', methods=['POST'])
def run_evaluate():
    """Run Evaluate phase on creators."""
    try:
        svc = get_sheets_service()

        # Read creators
        creators_data = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range="Creators!A2:P"
        ).execute()

        creators_rows = creators_data.get("values", [])
        creators = []

        for i, row in enumerate(creators_rows):
            if not row or row[0] == "":
                continue
            creator = {
                "creator_id": row[0],
                "platform": row[1],
                "handle": row[2],
                "display_name": row[3],
                "follower_count": int(row[6]) if len(row) > 6 and row[6] else 0,
                "tier": row[15] if len(row) > 15 else ""
            }
            creators.append(creator)

        # Group by tier
        tiers = {
            "A": [c for c in creators if c["tier"] == "A"],
            "B": [c for c in creators if c["tier"] == "B"],
            "C": [c for c in creators if c["tier"] == "C"],
            "Unrated": [c for c in creators if c["tier"] == ""]
        }

        return jsonify({
            "status": "success",
            "total_creators": len(creators),
            "tiers": {k: len(v) for k, v in tiers.items()},
            "tier_details": tiers
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# CREATORS MANAGEMENT
# ============================================================================

@app.route('/api/creators', methods=['GET'])
def get_creators():
    """Get all creators from sheet."""
    try:
        svc = get_sheets_service()

        creators_data = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range="Creators!A2:P"
        ).execute()

        creators_rows = creators_data.get("values", [])
        creators = []

        for row in creators_rows:
            if not row or row[0] == "":
                continue
            creator = {
                "creator_id": row[0],
                "platform": row[1],
                "handle": row[2],
                "display_name": row[3],
                "profile_url": row[4] if len(row) > 4 else "",
                "follower_count": int(row[6]) if len(row) > 6 and row[6] else 0,
                "email": row[10] if len(row) > 10 else "",
                "contact_status": row[12] if len(row) > 12 else "",
                "tier": row[15] if len(row) > 15 else ""
            }
            creators.append(creator)

        # Sort by follower count descending
        creators.sort(key=lambda x: x["follower_count"], reverse=True)

        return jsonify({
            "status": "success",
            "count": len(creators),
            "creators": creators
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/creators/<creator_id>', methods=['GET'])
def get_creator(creator_id):
    """Get single creator details."""
    try:
        svc = get_sheets_service()

        creators_data = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range="Creators!A2:P"
        ).execute()

        creators_rows = creators_data.get("values", [])

        for row in creators_rows:
            if row and row[0] == creator_id:
                creator = {
                    "creator_id": row[0],
                    "platform": row[1],
                    "handle": row[2],
                    "display_name": row[3],
                    "profile_url": row[4] if len(row) > 4 else "",
                    "bio_text": row[5] if len(row) > 5 else "",
                    "follower_count": int(row[6]) if len(row) > 6 and row[6] else 0,
                    "video_or_post_count": int(row[7]) if len(row) > 7 and row[7] else 0,
                    "location_hint": row[8] if len(row) > 8 else "",
                    "language_hint": row[9] if len(row) > 9 else "",
                    "email": row[10] if len(row) > 10 else "",
                    "phone": row[11] if len(row) > 11 else "",
                    "contact_status": row[12] if len(row) > 12 else "",
                    "tier": row[15] if len(row) > 15 else ""
                }
                return jsonify({"status": "success", "creator": creator})

        return jsonify({"status": "error", "message": "Creator not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# CONTENT GENERATION
# ============================================================================

@app.route('/api/content/<creator_id>', methods=['GET'])
def generate_content_brief(creator_id):
    """Generate content brief for a creator."""
    try:
        svc = get_sheets_service()

        # Get creator
        creators_data = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range="Creators!A2:P"
        ).execute()

        creator = None
        for row in creators_data.get("values", []):
            if row and row[0] == creator_id:
                creator = {
                    "handle": row[2],
                    "display_name": row[3],
                    "platform": row[1],
                    "follower_count": int(row[6]) if len(row) > 6 and row[6] else 0,
                    "video_or_post_count": int(row[7]) if len(row) > 7 and row[7] else 0,
                    "bio_text": row[5] if len(row) > 5 else "",
                    "language_hint": row[9] if len(row) > 9 else "",
                    "tier": row[15] if len(row) > 15 else ""
                }
                break

        if not creator:
            return jsonify({"status": "error", "message": "Creator not found"}), 404

        # Generate content ideas (simplified)
        ideas = [
            {
                "rank": 1,
                "title": "Live Trading Session",
                "platform": creator["platform"],
                "duration": "1.5–2 hours",
                "fit_score": 95,
                "topic": "Real-time trading execution",
                "cta": "Subscribe for live sessions"
            },
            {
                "rank": 2,
                "title": "Educational Deep Dive",
                "platform": creator["platform"],
                "duration": "8–12 minutes",
                "fit_score": 90,
                "topic": "Trading psychology or strategy",
                "cta": "Subscribe and enable notifications"
            }
        ]

        return jsonify({
            "status": "success",
            "creator": creator,
            "ideas": ideas,
            "calendar": "30-day content calendar available"
        })
    except Exception as e:
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
    """Serve React frontend."""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    """Handle 404 by serving index.html for React routing."""
    if request.path.startswith('/api'):
        return jsonify({"status": "error", "message": "Not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
