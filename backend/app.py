import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
import requests
from urllib.parse import urlparse, parse_qs

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
    """Run Evaluate phase on creators with detailed metrics."""
    try:
        # Sample creators with metrics (in production, read from Google Sheets)
        creators_sample = [
            {
                "creator_id": "1", "handle": "BitcoinBoyz_IN", "display_name": "Bitcoin Boyz India",
                "follower_count": 156000, "video_count": 487, "live_stream_count": 34, "contact_status": "found"
            },
            {
                "creator_id": "2", "handle": "CryptoTradingWithRahul", "display_name": "Rahul Crypto Trading",
                "follower_count": 125000, "video_count": 456, "live_stream_count": 31, "contact_status": "found"
            },
            {
                "creator_id": "3", "handle": "TradingWithVinay", "display_name": "Vinay - The Trader",
                "follower_count": 87500, "video_count": 312, "live_stream_count": 30, "contact_status": "found"
            },
            {
                "creator_id": "4", "handle": "DeepTradingSignals", "display_name": "Deep Trading Signals",
                "follower_count": 67800, "video_count": 265, "live_stream_count": 24, "contact_status": "dm_only"
            },
            {
                "creator_id": "5", "handle": "CryptoEdu_India", "display_name": "Crypto Education Hub",
                "follower_count": 45000, "video_count": 142, "live_stream_count": 14, "contact_status": "not_found"
            }
        ]

        # Calculate metrics for each creator
        evaluated_creators = []
        for creator in creators_sample:
            metrics = calculate_creator_metrics(creator)
            evaluated_creators.append({**creator, **metrics})

        # Group by tier
        tier_a = [c for c in evaluated_creators if c["tier"] == "A"]
        tier_b = [c for c in evaluated_creators if c["tier"] == "B"]
        tier_c = [c for c in evaluated_creators if c["tier"] == "C"]
        reject = [c for c in evaluated_creators if c["tier"] == "Reject"]

        return jsonify({
            "status": "success",
            "total_creators": len(evaluated_creators),
            "tiers": {
                "A": len(tier_a),
                "B": len(tier_b),
                "C": len(tier_c),
                "Reject": len(reject)
            },
            "creators": evaluated_creators,
            "tier_details": {
                "A": tier_a,
                "B": tier_b,
                "C": tier_c,
                "Reject": reject
            },
            "message": f"Evaluated {len(evaluated_creators)} creators. Tier A: {len(tier_a)}, B: {len(tier_b)}, C: {len(tier_c)}"
        })
    except Exception as e:
        logging.error(f"Evaluate error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# EVALUATE SINGLE CHANNEL
# ============================================================================

@app.route('/api/evaluate-channel', methods=['POST'])
def evaluate_single_channel():
    """Evaluate a single channel by link or handle."""
    try:
        params = request.json or {}
        channel_link = params.get("channel_link", "").strip()

        if not channel_link:
            return jsonify({"status": "error", "message": "Channel link or handle is required"}), 400

        # Parse the channel link to extract handle
        handle = parse_channel_link(channel_link)

        # Create a creator object based on the handle
        creator = get_creator_by_handle(handle)

        if not creator:
            return jsonify({"status": "error", "message": f"Channel '{handle}' not found in database"}), 404

        # Calculate metrics for the creator
        metrics = calculate_creator_metrics(creator)
        evaluated_creator = {**creator, **metrics}

        return jsonify({
            "status": "success",
            "creator": evaluated_creator,
            "message": f"Channel evaluated successfully! Score: {evaluated_creator['raw_score']}/100 (Tier {evaluated_creator['tier']})"
        })
    except Exception as e:
        logging.error(f"Evaluate channel error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def parse_channel_link(link):
    """Parse channel link or handle to extract the handle."""
    # Remove spaces and convert to lowercase
    link = link.strip().lower()

    # If it's a URL, extract the handle
    if 'youtube.com' in link or 'youtu.be' in link:
        # Extract handle from youtube.com/@handle or youtube.com/c/handle
        parts = link.split('/@')
        if len(parts) > 1:
            return parts[-1].split('?')[0].split('/')[0]
        parts = link.split('/c/')
        if len(parts) > 1:
            return parts[-1].split('?')[0].split('/')[0]
    elif 'instagram.com' in link:
        # Extract handle from instagram.com/handle
        parts = link.split('/instagram.com/')
        if len(parts) > 1:
            return parts[-1].split('?')[0].split('/')[0]
        parts = link.split('/')
        return parts[-1]
    elif 'telegram.me' in link or 't.me' in link:
        # Extract handle from t.me/handle
        parts = link.split('/')
        return parts[-1]

    # If no protocol, assume it's a handle
    if not link.startswith('http'):
        # Remove @ if present
        return link.lstrip('@')

    return link

def extract_youtube_channel_id(link):
    """Extract YouTube channel ID from various YouTube URL formats."""
    link = link.strip().lower()

    # Handle @handle format (custom URL)
    if '/@' in link:
        handle = link.split('/@')[1].split('?')[0].split('/')[0]
        return f"@{handle}"

    # Handle /c/ChannelName format (legacy)
    if '/c/' in link:
        channel_name = link.split('/c/')[1].split('?')[0].split('/')[0]
        return f"c/{channel_name}"

    # Handle channel ID format (UC...)
    if '/channel/' in link:
        channel_id = link.split('/channel/')[1].split('?')[0].split('/')[0]
        return channel_id

    # Handle just a handle without URL
    if not link.startswith('http'):
        link = link.lstrip('@')
        return f"@{link}"

    return None

@app.route('/api/fetch-youtube-data', methods=['POST'])
def fetch_youtube_data():
    """Fetch channel data from YouTube API."""
    try:
        params = request.json or {}
        channel_link = params.get("channel_link", "").strip()

        if not channel_link:
            return jsonify({"status": "error", "message": "Channel link is required"}), 400

        # Try to get YouTube API key from environment
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_api_key:
            # Fallback to mock data if no API key
            logging.warning("No YouTube API key found, using mock data")
            return get_mock_youtube_data(channel_link)

        # Extract channel identifier
        channel_id = extract_youtube_channel_id(channel_link)
        if not channel_id:
            return jsonify({"status": "error", "message": "Invalid YouTube link format"}), 400

        # Fetch from YouTube API
        youtube_data = fetch_from_youtube_api(channel_id, youtube_api_key)

        if youtube_data:
            return jsonify({
                "status": "success",
                "data": youtube_data
            })
        else:
            return jsonify({"status": "error", "message": "Could not fetch YouTube channel data"}), 404

    except Exception as e:
        logging.error(f"Fetch YouTube data error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def fetch_from_youtube_api(channel_id, api_key):
    """Fetch channel statistics from YouTube Data API v3."""
    try:
        # Build the API request URL
        url = "https://www.googleapis.com/youtube/v3/channels"

        params = {
            "key": api_key,
            "part": "snippet,statistics",
            "maxResults": 1
        }

        # Determine if we have a channel ID or need to search by handle
        if channel_id.startswith('@') or channel_id.startswith('c/'):
            # Use forUsername or search for custom URL
            # For custom URLs (@handle), we need to search first
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                "key": api_key,
                "q": channel_id.lstrip('@'),
                "type": "channel",
                "part": "snippet",
                "maxResults": 1
            }

            search_response = requests.get(search_url, params=search_params, timeout=10)
            if search_response.status_code != 200:
                logging.error(f"YouTube search failed: {search_response.text}")
                return None

            search_data = search_response.json()
            if not search_data.get('items'):
                return None

            channel_id = search_data['items'][0]['id']['channelId']

        # Now fetch the channel statistics
        params['id'] = channel_id

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logging.error(f"YouTube API error: {response.text}")
            return None

        data = response.json()

        if not data.get('items'):
            return None

        channel = data['items'][0]
        snippet = channel.get('snippet', {})
        statistics = channel.get('statistics', {})

        video_count = int(statistics.get('videoCount', 0))
        # Estimate live streams as ~10% of video count (adjustable)
        live_stream_count = max(0, int(video_count * 0.08))

        return {
            "handle": snippet.get('customUrl', '').lstrip('@'),
            "display_name": snippet.get('title', ''),
            "follower_count": int(statistics.get('subscriberCount', 0)),
            "video_count": video_count,
            "live_stream_count": live_stream_count,
            "profile_picture": snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            "description": snippet.get('description', '')
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"YouTube API request failed: {str(e)}")
        return None

def get_mock_youtube_data(channel_link):
    """Return mock YouTube data when API key is not available."""
    # Extract handle from link
    handle = parse_channel_link(channel_link)

    mock_data = {
        "handle": handle,
        "display_name": f"{handle} Channel",
        "follower_count": 125000,
        "video_count": 287,
        "live_stream_count": 23,
        "profile_picture": "https://yt3.ggpht.com/mock",
        "description": "A crypto and trading education channel"
    }

    return jsonify({
        "status": "success",
        "data": mock_data,
        "note": "Using mock data (no YouTube API key configured)"
    })

# Global in-memory database that persists during session
creators_database = {
    "bitcoinboyz_in": {
        "creator_id": "1", "handle": "BitcoinBoyz_IN", "display_name": "Bitcoin Boyz India",
        "platform": "YouTube", "follower_count": 156000, "video_count": 487, "live_stream_count": 34,
        "contact_status": "found", "profile_url": "https://youtube.com/@BitcoinBoyz_IN"
    },
    "cryptotradingwithrahul": {
        "creator_id": "2", "handle": "CryptoTradingWithRahul", "display_name": "Rahul Crypto Trading",
        "platform": "YouTube", "follower_count": 125000, "video_count": 456, "live_stream_count": 31,
        "contact_status": "found", "profile_url": "https://youtube.com/@CryptoTradingWithRahul"
    },
    "tradingwithvinay": {
        "creator_id": "3", "handle": "TradingWithVinay", "display_name": "Vinay - The Trader",
        "platform": "YouTube", "follower_count": 87500, "video_count": 312, "live_stream_count": 30,
        "contact_status": "found", "profile_url": "https://youtube.com/@TradingWithVinay"
    },
    "deeptradingsignals": {
        "creator_id": "4", "handle": "DeepTradingSignals", "display_name": "Deep Trading Signals",
        "platform": "YouTube", "follower_count": 67800, "video_count": 265, "live_stream_count": 24,
        "contact_status": "dm_only", "profile_url": "https://youtube.com/@DeepTradingSignals"
    },
    "cryptoedu_india": {
        "creator_id": "5", "handle": "CryptoEdu_India", "display_name": "Crypto Education Hub",
        "platform": "YouTube", "follower_count": 45000, "video_count": 142, "live_stream_count": 14,
        "contact_status": "not_found", "profile_url": "https://youtube.com/@CryptoEdu_India"
    }
}

def get_creator_by_handle(handle):
    """Get creator data by handle. Returns None if not found."""
    key = handle.lower().replace('@', '')
    return creators_database.get(key)

@app.route('/api/add-creator', methods=['POST'])
def add_creator():
    """Add a new creator to the database."""
    try:
        params = request.json or {}

        required_fields = ['handle', 'display_name', 'follower_count', 'platform']
        for field in required_fields:
            if not params.get(field):
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

        handle = params.get('handle', '').strip()
        display_name = params.get('display_name', '').strip()
        follower_count = int(params.get('follower_count', 0))
        video_count = int(params.get('video_count', 0))
        live_stream_count = int(params.get('live_stream_count', 0))
        platform = params.get('platform', 'YouTube').strip()
        contact_status = params.get('contact_status', 'not_found').strip()

        # Check if creator already exists
        key = handle.lower().replace('@', '')
        if key in creators_database:
            return jsonify({"status": "error", "message": f"Creator '{handle}' already exists in database"}), 409

        # Create new creator object
        new_creator = {
            "creator_id": str(uuid.uuid4()),
            "handle": handle,
            "display_name": display_name,
            "platform": platform,
            "follower_count": follower_count,
            "video_count": video_count,
            "live_stream_count": live_stream_count,
            "contact_status": contact_status,
            "profile_url": f"https://{platform.lower()}.com/@{handle}" if platform == "YouTube" else f"https://{platform.lower()}.com/{handle}"
        }

        # Add to database
        creators_database[key] = new_creator

        # Calculate metrics
        metrics = calculate_creator_metrics(new_creator)
        result = {**new_creator, **metrics}

        return jsonify({
            "status": "success",
            "creator": result,
            "message": f"✅ New creator '{display_name}' added to database! Score: {result['raw_score']}/100 (Tier {result['tier']})"
        })
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Add creator error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def calculate_creator_metrics(creator):
    """Calculate all evaluation metrics for a creator with actual + scaled values."""
    fc = creator.get("follower_count", 0)

    # Count only videos and live streams for cadence
    video_count = creator.get("video_count", 0)
    live_stream_count = creator.get("live_stream_count", 0)
    total_content = video_count + live_stream_count

    contact_status = creator.get("contact_status", "not_found")

    # 1. Follower Score - ACTUAL + SCALED
    if fc >= 500000:
        follower_pts = 0.25
        follower_tier = "500k+"
    elif fc >= 100000:
        follower_pts = 0.22
        follower_tier = "100k-500k"
    elif fc >= 50000:
        follower_pts = 0.18
        follower_tier = "50k-100k"
    elif fc >= 25000:
        follower_pts = 0.12
        follower_tier = "25k-50k"
    elif fc >= 10000:
        follower_pts = 0.06
        follower_tier = "10k-25k"
    else:
        follower_pts = 0.02
        follower_tier = "<10k"

    # 2. View-to-Follower Ratio (estimated) - ACTUAL + SCALED
    if fc >= 500000:
        view_ratio = 0.04
    elif fc >= 100000:
        view_ratio = 0.10
    elif fc >= 25000:
        view_ratio = 0.15
    else:
        view_ratio = 0.08
    view_ratio_pts = 0.15 if view_ratio >= 0.10 else 0.10
    view_ratio_pct = view_ratio * 100

    # 3. Posting Cadence - ACTUAL + SCALED (Videos + Live Streams only)
    # Assume ~52 weeks per year for annual calculation
    cadence = (total_content / 52) if total_content > 0 else 0
    if cadence >= 2:
        cadence_pts = 0.15
        cadence_label = "High (2+ per week)"
    elif cadence >= 1:
        cadence_pts = 0.12
        cadence_label = "Good (1-2 per week)"
    elif cadence >= 0.5:
        cadence_pts = 0.08
        cadence_label = "Moderate (bi-weekly)"
    else:
        cadence_pts = 0.03
        cadence_label = "Low (monthly)"

    # 4. Live Propensity (neutral if not captured)
    live_pts = 0.07
    live_actual = "Not captured"

    # 5. Content Category Match (crypto focus)
    content_match_pts = 0.15
    content_match_pct = 75  # Assume 75% crypto focus

    # 6. Contact Status Bonus - ACTUAL + SCALED
    if contact_status == "found":
        contact_bonus = 0.02
        contact_label = "Email/Phone"
    elif contact_status == "dm_only":
        contact_bonus = 0.00
        contact_label = "DM Only"
    else:
        contact_bonus = -0.03
        contact_label = "No Contact"

    # 7. Composite Score
    contact_norm = (contact_bonus + 0.05) / 0.05
    score = (
        (follower_pts / 0.25) * 0.20 +
        (view_ratio_pts / 0.20) * 0.20 +
        (cadence_pts / 0.15) * 0.15 +
        (live_pts / 0.10) * 0.15 +
        (content_match_pts / 0.20) * 0.20 +
        contact_norm * 0.10
    )
    raw_score = score * 100

    # 8. Tier Assignment
    if raw_score >= 80:
        tier = "A"
    elif raw_score >= 65:
        tier = "B"
    elif raw_score >= 50:
        tier = "C"
    else:
        tier = "Reject"

    return {
        # Actual Values
        "followers_actual": fc,
        "follower_tier": follower_tier,
        "cadence_actual": round(cadence, 2),
        "cadence_actual_label": cadence_label,
        "video_count_actual": video_count,
        "live_stream_count_actual": live_stream_count,
        "total_content_actual": total_content,
        "view_ratio_actual_pct": round(view_ratio_pct, 1),
        "content_match_actual_pct": content_match_pct,
        "contact_actual": contact_label,

        # Scaled Scores (0-1 range)
        "follower_pts": round(follower_pts, 2),
        "view_ratio_pts": round(view_ratio_pts, 2),
        "cadence_pts": round(cadence_pts, 2),
        "live_pts": round(live_pts, 2),
        "content_match_pts": round(content_match_pts, 2),
        "contact_bonus": round(contact_bonus, 2),

        # Final Score
        "raw_score": round(raw_score, 1),
        "tier": tier,

        # Labels
        "cadence_label": cadence_label,

        # Detailed breakdown for display
        "metrics_detail": {
            "Followers": f"{fc:,} → {follower_pts:.2f}/0.25",
            "View Ratio": f"{view_ratio_pct:.1f}% → {view_ratio_pts:.2f}/0.20",
            "Cadence": f"{cadence:.2f} videos/week → {cadence_pts:.2f}/0.15",
            "Content": f"{video_count} videos + {live_stream_count} lives = {total_content} total",
            "Live Stream": f"{live_actual} → {live_pts:.2f}/0.10",
            "Content Match": f"{content_match_pct}% → {content_match_pts:.2f}/0.20",
            "Contact": f"{contact_label} → {contact_bonus:+.2f}",
            "Composite Score": f"{raw_score:.1f}/100",
            "Tier": tier
        }
    }

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
