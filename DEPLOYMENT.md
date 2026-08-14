# Deployment Guide — Creator Partnerships Agent

## Quick Start (5 minutes)

### Phase 1: Prepare GitHub Repository

1. Create new GitHub repo at https://github.com/new
   - Name: `creator-partnerships-agent`
   - Description: "Creator partnerships management platform"
   - Public (or Private if preferred)
   - Initialize empty (no README/gitignore, we have those)

2. Clone this repo and push to GitHub:
```bash
cd /path/to/creator-partnerships-app
git remote add origin https://github.com/YOUR-USERNAME/creator-partnerships-agent.git
git branch -M main
git push -u origin main
```

### Phase 2: Deploy to Render (3 minutes)

1. **Go to Render**: https://render.com
   - Sign up with GitHub account (easier)
   - Authorize GitHub access

2. **Create new Web Service**:
   - Dashboard → "New" → "Web Service"
   - Select your `creator-partnerships-agent` repo
   - Click "Connect"

3. **Configure deployment**:
   ```
   Name:                    creator-partnerships-agent
   Environment:             Python 3
   Build Command:           pip install -r requirements.txt
   Start Command:           cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   Plan:                    Free (or Starter/Standard for production)
   ```

4. **Add Environment Variable**:
   - Click "Advanced" (or skip to Settings after creation)
   - Add new environment variable:
     - Key: `GOOGLE_SERVICE_ACCOUNT_KEY`
     - Value: [Paste your Google service account JSON]

   **Where to get service account JSON?**
   - From your local machine: `cat ~/rm-uploader/sa.json`
   - Copy the entire JSON content (including outer braces)
   - Paste into Render environment variable value

5. **Click "Create Web Service"**
   - Wait 2–3 minutes for build & deploy
   - You'll see:
     ```
     ✓ Build successful
     ✓ Service deployed
     ✓ Live at: https://creator-partnerships-agent.onrender.com
     ```

### Phase 3: Verify Deployment (1 minute)

1. **Test the API**:
   ```bash
   curl https://creator-partnerships-agent.onrender.com/api/health
   # Should return: {"status": "ok", "timestamp": "..."}
   ```

2. **Visit the Dashboard**:
   - Open: `https://creator-partnerships-agent.onrender.com`
   - You should see the Creator Partnerships Agent interface
   - Click "🔄 Refresh" button
   - If creators load from your Google Sheet, you're live! ✅

### Phase 4: Ongoing Management

**View Logs**:
```
Render Dashboard → creator-partnerships-agent → Logs
```

**Redeploy after code changes**:
```bash
git add .
git commit -m "Update feature X"
git push origin main
# Render auto-redeploys ~30 seconds after push
```

**Update environment variables**:
- Render Dashboard → Settings → Environment Variables
- Edit the value, save → auto-redeploy

**Scale up (production)**:
- Render Dashboard → Settings → Plan
- Upgrade from Free → Starter ($7/month) or Standard ($25+/month)
- Free tier: 15 min auto-sleep after inactivity; Starter+ are always-on

---

## Troubleshooting

### Error: "Build failed"
**Check logs** → Render Dashboard → Logs
- Common: Missing Python dependency (add to requirements.txt)
- Common: Wrong start command in Procfile

### Error: "GOOGLE_SERVICE_ACCOUNT_KEY not set"
1. Render Dashboard → Settings → Environment Variables
2. Verify the variable is named exactly `GOOGLE_SERVICE_ACCOUNT_KEY`
3. Verify value is the full JSON (not just a URL or partial JSON)
4. Save, then redeploy

### Error: "Permission denied" on Google Sheets
1. Verify Google Sheet is shared with service account email:
   `google-sheets-api@burnished-fold-500408-r1.iam.gserviceaccount.com`
2. Share permission must be **Editor** (not Viewer or Commenter)
3. Open sheet → Share → Add email → Editor → Share

### Error: "Creators not loading on dashboard"
1. Check Render logs for API errors
2. Verify the Google Sheet ID is correct in `backend/app.py` line 11
   - Sheet ID should be: `1zc4XB4aVutf8JubEf_vQrSvpzdr7lTfG2G_sVYEJKwk`
3. Verify the Creators tab exists in your Google Sheet

### App is slow / timeouts
- Free tier has limited CPU/RAM
- For production, upgrade to Starter plan
- Google Sheets API has rate limit: 300 req/min (unlikely to hit)

---

## DNS & Custom Domain (Optional)

1. **Buy a domain** (Namecheap, GoDaddy, etc.)
   - Example: `creator-partnerships.com`

2. **Add to Render**:
   - Render Dashboard → Settings → Custom Domains
   - Click "Add Custom Domain"
   - Enter domain (e.g., `app.creator-partnerships.com`)
   - Follow DNS instructions (add CNAME record)

3. **Wait 24–48 hours** for DNS propagation

---

## Monitoring & Alerts (Optional)

**Render built-in monitoring**:
- Dashboard shows CPU, memory, response times
- Logs auto-archive (viewable in dashboard)

**Set up email alerts** (Starter+ plans):
- Settings → Alerts
- Create alert for deployment failures, high error rates, etc.

---

## Backup & Version Control

**GitHub is your backup**:
- Every push to main automatically triggers Render redeploy
- All code changes are version-controlled
- Rollback: Revert git commit, push (Render redeploys old version)

**Google Sheets is your data backup**:
- All creator data lives in Google Sheets
- Render only reads/writes to it (no local DB)
- Safe to delete Render service and recreate (data is unchanged)

---

## Next: Add More Features

Once live, extend the app:

1. **Add Collaborate phase**
   - Edit `backend/app.py` → add `@app.route('/api/collaborate', ...)`
   - Draft outreach emails
   - Log emails sent to Google Sheets

2. **Add Track phase**
   - Monitor deliverables
   - Real-time performance metrics

3. **Add authentication**
   - Protect dashboard with login (if team-access needed)
   - Use Flask-Login or OAuth

4. **Upgrade to production plan**
   - Switch from Free → Starter ($7/month)
   - Always-on (no 15 min auto-sleep)
   - Larger database quota

---

## Commands Reference

**Deploy**:
```bash
git add .
git commit -m "Your message"
git push origin main
```

**Test locally before pushing**:
```bash
cd backend
python app.py
# Visit http://localhost:5000
```

**View service account key**:
```bash
cat ~/rm-uploader/sa.json
```

**View Render logs live** (if you have Render CLI):
```bash
render logs creator-partnerships-agent
```

---

## Success Checklist

- [ ] GitHub repo created and code pushed
- [ ] Render app deployed successfully
- [ ] Environment variable set (GOOGLE_SERVICE_ACCOUNT_KEY)
- [ ] Google Sheet shared with service account (Editor)
- [ ] Dashboard loads at https://creator-partnerships-agent.onrender.com
- [ ] "Refresh" button works and loads creators
- [ ] /api/health endpoint returns OK
- [ ] Logs are clean (no errors)

If all checked: **You're live! 🚀**

---

## Getting Help

**Render Support**: https://render.com/support
**GitHub Issues**: Create issue in your repo
**CoinSwitch**: Slack #engineering (tag Darshan)

Deployment takes ~5 minutes. You've got this! 💪
