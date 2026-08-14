# ⚡ Fix: "Not Found" Error on Render

Your app is showing "Not Found" because the frontend files aren't being served correctly. This is **fixed**. Just push the updated code.

## 🔧 What Was Wrong

The Flask app was looking for frontend files in a `frontend/build/` folder that doesn't exist.

**Fixed**: Updated `backend/app.py` to serve `frontend/index.html` correctly.

## 🚀 How to Fix (30 seconds)

### Step 1: Push the fixed code

Copy-paste your GitHub repo URL and run:

```bash
cd /tmp/creator-partnerships-app

git push origin main
```

(Replace with your actual repo URL if needed)

**If you get "rejected":**
```bash
git push origin main --force
```

### Step 2: Redeploy on Render

1. Go to Render Dashboard
2. Click on `creator-partnerships-agent`
3. You should see **deployment in progress** (auto-triggered by git push)
4. Wait 2–3 minutes for build to complete
5. You'll see: `✓ Deployed`

### Step 3: Visit your app

- Refresh: `https://creator-partnerships-agent.onrender.com`
- You should now see the **Creator Partnerships Agent** dashboard ✅

---

## ✅ Troubleshooting

### Still showing "Not Found"?

1. **Check Render Logs**:
   - Dashboard → `creator-partnerships-agent` → **Logs**
   - Look for any error messages
   - Share the error with me

2. **Check Render Events**:
   - Dashboard → `creator-partnerships-agent` → **Events**
   - Confirm deployment completed successfully

3. **Hard refresh browser**:
   ```
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (Mac)
   ```

4. **Wait a moment**:
   - Render might still be starting the service
   - Free tier takes ~10 seconds to boot

### Getting "Permission denied" on GitHub push?

```bash
# Use HTTPS (no SSH needed)
git remote set-url origin https://github.com/YOUR-USERNAME/creator-partnerships-agent.git
git push origin main
```

### Build is failing?

Check Render logs for error. Common issues:
- Missing Google service account key (check Environment Variables)
- Python dependency issue (shouldn't happen)
- Wrong start command (shouldn't happen)

---

## 📝 What Changed

**File**: `backend/app.py`

**Before**:
```python
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
```

**After**:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# ... and updated serve_frontend() to use FRONTEND_DIR directly
```

This tells Flask to serve HTML files from the correct `frontend/` folder (where `index.html` actually is).

---

## 🎯 Expected Result

After pushing and waiting for deployment:
- ✅ Dashboard loads at `https://creator-partnerships-agent.onrender.com`
- ✅ Buttons are clickable (Hunt, Evaluate, Content, Creators, Refresh)
- ✅ "Refresh" button loads creators from your Google Sheet
- ✅ No "Not Found" error

---

## ⏱️ Timeline

1. **Push code**: 5 seconds
2. **Render builds**: 1–2 minutes
3. **Deployment**: 30 seconds
4. **Live**: 2–3 minutes total

**Total**: ~3 minutes from push to live ✅

Let me know when you've pushed and I'll help verify it's working!
