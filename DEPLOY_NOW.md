# ⚡ DEPLOY NOW — 3-Step Guide

Your app is ready. Follow these exact steps to deploy live in **5 minutes**.

---

## STEP 1: Create GitHub Repository (2 minutes)

### 1.1 Create the repo
1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `creator-partnerships-agent`
   - **Description**: "Creator partnerships management platform"
   - **Public** or **Private** (your choice)
   - Leave everything else default
3. Click **Create repository**

### 1.2 Push code to GitHub
Copy-paste these commands in your terminal:

```bash
cd /tmp/creator-partnerships-app

git remote add origin https://github.com/YOUR-USERNAME/creator-partnerships-agent.git

git branch -M main

git push -u origin main
```

**Replace `YOUR-USERNAME` with your actual GitHub username** (e.g., `darshan-d`)

**Expected output:**
```
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 8 threads.
Compressing objects: 100% (7/7), done.
Writing objects: 100% (9/9), 3.45 KiB | 1.15 MiB/s, done.
Total 9 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR-USERNAME/creator-partnerships-agent.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **Code is now on GitHub**

---

## STEP 2: Deploy to Render (2 minutes)

### 2.1 Create Render account
1. Go to https://render.com
2. Click **Sign Up**
3. Click **Continue with GitHub**
4. Authorize Render to access GitHub
5. Done!

### 2.2 Create Web Service
1. In Render dashboard, click **New** → **Web Service**
2. Click **Connect repository**
3. Select `creator-partnerships-agent` from the list
4. Click **Connect**

### 2.3 Configure service
Fill in exactly these values:

| Field | Value |
|-------|-------|
| **Name** | `creator-partnerships-agent` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app` |
| **Plan** | `Free` |

### 2.4 Add Environment Variable
1. Scroll down to **Environment**
2. Click **Add Environment Variable**
3. Fill in:
   - **Key**: `GOOGLE_SERVICE_ACCOUNT_KEY`
   - **Value**: [Paste your service account JSON]

**Where to get the service account JSON:**
```bash
cat ~/rm-uploader/sa.json
```
Copy the entire output (starting with `{` and ending with `}`) and paste into Render.

### 2.5 Deploy
1. Click **Create Web Service**
2. Wait 2–3 minutes (you'll see build status)
3. When done, you'll see:
   ```
   ✓ Build successful
   ✓ Deployed
   https://creator-partnerships-agent.onrender.com
   ```

Copy that URL — **that's your app!**

✅ **App is now live on Render**

---

## STEP 3: Verify Deployment (1 minute)

### 3.1 Test the API
```bash
curl https://creator-partnerships-agent.onrender.com/api/health
```

Should return:
```json
{"status": "ok", "timestamp": "2026-08-14T..."}
```

### 3.2 Visit the dashboard
1. Open in browser: `https://creator-partnerships-agent.onrender.com`
2. You should see the **Creator Partnerships Agent** dashboard
3. Click the **🔄 Refresh** button
4. If creators load from your Google Sheet, you're **live!** ✅

---

## ✅ Success Checklist

- [ ] GitHub repo created at `https://github.com/YOUR-USERNAME/creator-partnerships-agent`
- [ ] Code pushed with `git push`
- [ ] Render account created
- [ ] Web Service created in Render
- [ ] `GOOGLE_SERVICE_ACCOUNT_KEY` environment variable added
- [ ] Deployment successful (Render shows "Deployed")
- [ ] Dashboard loads at `https://creator-partnerships-agent.onrender.com`
- [ ] **Refresh** button works and loads creators

**If all checked: 🎉 YOU'RE LIVE!**

---

## 🔧 Troubleshooting

### "Permission denied" on Google Sheets
→ Share your Creator Partnerships sheet with: `google-sheets-api@burnished-fold-500408-r1.iam.gserviceaccount.com`
→ Give **Editor** permission

### "Creators not loading"
→ Check Render logs: Dashboard → Logs
→ Verify `GOOGLE_SERVICE_ACCOUNT_KEY` is set correctly

### "Build failed"
→ Check Render logs for the error
→ Most common: Python dependency missing (shouldn't happen, but check requirements.txt)

### "App times out"
→ Free tier takes a moment to start (first request is slow)
→ Subsequent requests are fast

---

## 📚 After Deployment

**View your app**:
- Frontend: `https://creator-partnerships-agent.onrender.com`
- API docs: `https://creator-partnerships-agent.onrender.com/api/health`

**Make changes**:
```bash
# Edit code locally
nano backend/app.py

# Commit and push
git add .
git commit -m "Your change"
git push origin main

# Render auto-redeploys ~30 seconds after push
```

**Monitor**:
- Render Dashboard → Logs (see all requests & errors)
- Render Dashboard → Metrics (CPU, memory, response time)

---

## 🚀 You're Ready!

Everything is prepared. Just:
1. Create GitHub repo
2. Push code
3. Deploy to Render
4. Add environment variable
5. Visit your app

**Total time: 5 minutes**

Let me know when you're done and I'll help with next steps! 🎉
