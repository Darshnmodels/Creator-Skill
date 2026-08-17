# Google Sheets Integration Setup

## Overview

Hunt results are now stored in Google Sheets for persistent tracking and history. This guide explains how to set up the integration.

## Prerequisites

- Google Cloud Project with Sheets API enabled
- Service Account with JSON key file
- Google Drive access to create and manage sheets

## Setup Steps

### 1. Create a New Google Sheet for Hunt Results

1. Go to [Google Sheets](https://sheets.google.com)
2. Click "Create new spreadsheet"
3. Name it: `Creator Partners - Hunt Results`
4. Copy the spreadsheet ID from the URL (format: `/spreadsheets/d/{SHEET_ID}/`)

### 2. Set Up Column Headers

In the new sheet, add these headers in row 1:

```
A: Hunt ID
B: Timestamp
C: Vertical
D: Platforms
E: Num Creators
F: Found Count
G: Contact Found
H: Sample Creators (JSON)
I: Status
```

### 3. Share with Service Account

1. Open the sheet
2. Click "Share" button
3. Add the service account email: `google-sheets-api@burnished-fold-500408-r1.iam.gserviceaccount.com`
4. Grant "Editor" permissions
5. Copy the **Spreadsheet ID** from the URL

### 4. Set Environment Variable

**For Render Deployment:**
1. Go to Render Dashboard → Creator-Skill Service
2. Click "Environment" tab
3. Add new variable:
   - Key: `HUNT_RESULTS_SHEET_ID`
   - Value: (paste the Spreadsheet ID from step 3)
4. Save and redeploy

**For Local Development:**
```bash
export HUNT_RESULTS_SHEET_ID="your-sheet-id-here"
python backend/app.py
```

### 5. Set Up Service Account Key

The backend looks for the service account key at:
```
~/.config/creator-partnerships/sa.json
```

If using a different path, update in `app.py`:
```python
SA_KEY_PATH = os.path.expanduser('~/your/path/sa.json')
```

## File Structure

```
~/.config/creator-partnerships/
└── sa.json                    # Google Service Account key
```

## How It Works

### Hunt Flow

1. User runs a hunt in the web app
2. Backend generates mock creators
3. Results are **automatically saved** to Google Sheets
4. Hunt ID, timestamp, and parameters are stored
5. User can view/export results

### Storage Format

Each hunt row contains:
- **Hunt ID**: Unique identifier (UUID)
- **Timestamp**: When the hunt was run
- **Vertical**: Crypto, Equities, Forex, Options, or Fintech
- **Platforms**: YouTube, Instagram, Telegram, Twitter
- **Num Creators**: Requested count
- **Found Count**: Total discovered
- **Contact Found**: With contact info
- **Sample Creators**: First 5 creators as JSON (for quick preview)
- **Status**: completed/failed/pending

### Retrieving Results

**Frontend endpoints:**
- `GET /api/hunt-results?limit=10` — Get last 10 hunts
- `GET /api/hunt/{hunt_id}` — Get specific hunt details

## Troubleshooting

### "Google Sheets API not initialized"

- Check service account key file exists at `~/.config/creator-partnerships/sa.json`
- Verify the JSON file is valid (not corrupted)
- Ensure sheets API is enabled in Google Cloud Console

### "Permission denied" when writing to sheets

- Confirm sheet is shared with the service account email
- Check that the account has "Editor" role
- Verify `HUNT_RESULTS_SHEET_ID` is correct

### No hunt history appears

- Click "Load Previous Hunt Results" button in Results tab
- Check that at least one hunt has been run
- Verify the sheet exists and is accessible

## Security Notes

- Service account key has **Editor access** to the Hunt Results sheet only
- Key file should be **kept private** and never committed to git
- For production, use environment variables (already configured on Render)
- Consider using separate service accounts for different environments

## Sample Data Structure

When a hunt completes, this data is written to Google Sheets:

```json
{
  "hunt_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-08-17T14:30:45.123456",
  "vertical": "crypto",
  "platforms": "youtube",
  "num_creators": 1000,
  "found_count": 1150,
  "contact_found": 748,
  "creators": [
    {
      "creator_id": "1",
      "handle": "BitcoinBoyzIN",
      "display_name": "Bitcoin Boyz India",
      "followers": 50000,
      "engagement_rate": 4.8,
      "content_match": 95,
      "tier": "A"
    },
    ...
  ],
  "status": "completed"
}
```

## Next Steps

1. Create the Google Sheet
2. Set the `HUNT_RESULTS_SHEET_ID` environment variable
3. Deploy to Render
4. Run a hunt and verify it appears in the sheet
5. Use "Load Previous Hunt Results" to retrieve saved hunts

## Questions?

For issues with Google Sheets integration, check:
- Service account permissions
- Spreadsheet sharing settings
- Backend logs for API errors
- Environment variable configuration
