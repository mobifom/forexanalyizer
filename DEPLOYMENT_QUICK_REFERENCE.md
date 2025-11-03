# 🚀 Streamlit Deployment Quick Reference

## Your GitHub Repository
```
https://github.com/mobifom/forexanalyizer
```

## Deploy to Streamlit Cloud

### Step 1: Go to Streamlit Cloud
**URL:** https://share.streamlit.io/

### Step 2: Sign in with GitHub
Click "Sign in" and authorize your GitHub account

### Step 3: Create New App
- Click "**New app**" button
- **Repository:** `mobifom/forexanalyizer`
- **Branch:** `main`
- **Main file:** `app.py`
- Click "**Deploy!**"

### Step 4: Add Secrets (IMPORTANT!)
After deployment:
1. Click menu (⋮) → "**Settings**"
2. Go to "**Secrets**" tab
3. Add this in TOML format:

```toml
TWELVEDATA_API_KEY = "your_api_key_here"
```

4. Click "**Save**"
5. Click "**Reboot app**"

## Your App Will Be Live At:
```
https://mobifom-forexanalyizer-app-[random].streamlit.app
```

## Default Login Credentials

### Admin Account (Full Access)
- **Username:** `admin`
- **Password:** `admin123`

### User Account (Limited Access)
- **Username:** `user`
- **Password:** `user123`

⚠️ **Change these passwords immediately after first login!**

## Features by Role

### 👑 Admin Can:
- ✅ View all analysis and charts
- ✅ Refresh data (bypass cache)
- ✅ Train ML models
- ✅ Scan multiple pairs
- ✅ Manage users
- ✅ Change all settings

### 👤 User Can:
- ✅ View all analysis and charts
- ✅ Scan multiple pairs
- ❌ Cannot refresh data
- ❌ Cannot train models
- ❌ Cannot manage users

## Quick Links

- **GitHub Repo:** https://github.com/mobifom/forexanalyizer
- **Streamlit Cloud:** https://share.streamlit.io/
- **Deploy Direct:** https://share.streamlit.io/deploy
- **Streamlit Docs:** https://docs.streamlit.io/

## Troubleshooting

### API Key Not Working?
- Check secret name is exactly: `TWELVEDATA_API_KEY`
- Verify TOML format is correct (no extra quotes)
- Reboot the app after adding secrets

### App Won't Start?
- Check logs: Menu → "Manage app" → "Logs"
- Verify all files are in GitHub
- Check requirements.txt is complete

### Login Not Working?
- Default users are created automatically
- Try refreshing the page
- Check console logs for errors

## Need Help?

Full deployment guide: `STREAMLIT_DEPLOYMENT_GUIDE.md`
Authentication docs: `AUTHENTICATION_IMPLEMENTATION.md`
Project README: `README.md`

---

**Ready to deploy?** → https://share.streamlit.io/deploy

**Your Repo:** mobifom/forexanalyizer

**Main File:** app.py

**Branch:** main
