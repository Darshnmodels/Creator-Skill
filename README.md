# Creator Partnerships Agent

A full-stack web application for managing creator partnerships at CoinSwitch. Hunt, Evaluate, Create Content, Collaborate, and Track creator campaigns.

## Features

- **🔍 Hunt Phase**: Discover creators across YouTube, Instagram, Telegram, Twitter
- **📊 Evaluate Phase**: Score and tier creators (A/B/C) based on engagement metrics
- **📝 Content Generation**: Generate platform-specific content ideas and briefs
- **👥 Creator Management**: View all creators, details, and contact info
- **📈 Dashboard**: Real-time stats on creator reach, tiers, and performance

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build step required)
- **Database**: Google Sheets API
- **Hosting**: Render.com

## Local Development

### Prerequisites
- Python 3.8+
- Google service account with Sheets API enabled
- Git

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/creator-partnerships-agent.git
cd creator-partnerships-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
```

(Get the service account JSON from Google Cloud Console)

5. **Run the app**
```bash
cd backend
python app.py
```

Visit http://localhost:5000

## Deployment to Render

### Step 1: Create GitHub Repository

1. Create a new GitHub repo (e.g., `creator-partnerships-agent`)
2. Push this code:
```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/creator-partnerships-agent.git
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to https://render.com and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: `creator-partnerships-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
   - **Plan**: Free (or upgrade for production)

5. Add Environment Variable:
   - **Key**: `GOOGLE_SERVICE_ACCOUNT_KEY`
   - **Value**: Paste your Google service account JSON (get from `~/rm-uploader/sa.json`)

6. Click "Create Web Service" and wait for deployment (~3 min)

### Step 3: Verify Deployment

Once deployed:
1. Click the URL in Render dashboard
2. You should see the Creator Partnerships Agent dashboard
3. Test by clicking "🔄 Refresh" button

## API Endpoints

### Hunt Phase
```
POST /api/hunt
{
  "vertical": "crypto",
  "platforms": "youtube",
  "geography": "India (Hindi, English)",
  "follower_min": 10000,
  "follower_max": 999999
}
```

### Evaluate Phase
```
POST /api/evaluate
```

### Creators
```
GET /api/creators                    # List all creators
GET /api/creators/<creator_id>       # Get creator details
```

### Content Generation
```
GET /api/content/<creator_id>        # Generate content brief
```

### Health Check
```
GET /api/health                      # Service status
```

## Google Sheets Integration

The app reads/writes to Google Sheets:
- **Sheet ID**: `1zc4XB4aVutf8JubEf_vQrSvpzdr7lTfG2G_sVYEJKwk`
- **Tabs**:
  - `Creators`: All discovered creators
  - `Deals`: Commercial partnerships
  - `Deliverables`: Content deliverables tracking
  - `Hunt Runs`: Hunt phase metadata

The Google service account must have Editor access to this sheet.

## File Structure

```
creator-partnerships-agent/
├── backend/
│   └── app.py              # Flask app with all API endpoints
├── frontend/
│   └── index.html          # Single-page HTML frontend
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── render.yaml            # Render service definition
├── .gitignore
└── README.md
```

## Extending the App

### Adding New Phases

Edit `backend/app.py`:
1. Add a new `@app.route('/api/{phase}', methods=['POST'])` function
2. Implement the phase logic
3. Return JSON response

### Updating Frontend

Edit `frontend/index.html`:
1. Add a new tab in the HTML
2. Add JavaScript function to call the API endpoint
3. Add button in the nav to switch to the new tab

### Updating Google Sheets Integration

Edit `backend/app.py`:
- Use `svc.spreadsheets().values().get(...)` to read
- Use `svc.spreadsheets().values().update(...)` to write
- Use `svc.spreadsheets().values().append(...)` to add rows

## Troubleshooting

### "GOOGLE_SERVICE_ACCOUNT_KEY not set"
- Go to Render dashboard → Settings → Environment Variables
- Add the `GOOGLE_SERVICE_ACCOUNT_KEY` variable with your service account JSON

### "Permission denied" on Google Sheets
- Ensure the Google service account email is shared (Editor) on the target sheet
- Service account email: `google-sheets-api@burnished-fold-500408-r1.iam.gserviceaccount.com`

### Deployment fails
- Check Render logs: Dashboard → Web Service → Logs
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` points to correct start command

## Performance & Limits

- **Free Tier**: Limited to 0.5GB RAM, 100GB/month bandwidth
- **Google Sheets API**: 300 requests/minute (quota limit)
- **Creator List**: Optimized for up to 5,000 creators

For production scale-up, upgrade Render plan or migrate to PostgreSQL.

## Security Notes

- Service account key is stored in Render environment variables (encrypted at rest)
- All API calls require CORS validation
- Frontend runs on same domain (no external API calls)
- No user authentication (add if needed for team access)

## Next Steps

1. Deploy to Render (follow steps above)
2. Test all phases in the web UI
3. Connect to your creator partnership workflow
4. Add more phases (Collaborate, Track) as you expand

## Support

For questions or issues:
- Check Render logs
- Verify Google Sheets integration
- Review Flask app.py for API implementation
