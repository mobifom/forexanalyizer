# Streamlit Cloud Deployment Guide

## Your GitHub Repository URL
```
https://github.com/mobifom/forexanalyizer
```

## Step-by-Step Deployment Instructions

### 1. Push Latest Changes to GitHub

```bash
# Add the new authentication files
git add .
git commit -m "Add Streamlit deployment configuration"
git push forexanalyizer main
```

### 2. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io/

2. **Sign in with GitHub:**
   - Click "Sign in" and authorize with your GitHub account

3. **Create New App:**
   - Click "New app" button
   - Select your repository: `mobifom/forexanalyizer`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

### 3. Configure Secrets (IMPORTANT!)

After deployment, you need to add your API keys as secrets:

1. **Go to App Settings:**
   - Click the menu (⋮) on your deployed app
   - Select "Settings"

2. **Add Secrets:**
   - Go to "Secrets" section
   - Add the following in TOML format:

```toml
# API Keys
TWELVEDATA_API_KEY = "your_api_key_here"

# Optional: Add other configuration
[api]
twelvedata_key = "your_api_key_here"
```

3. **Save and Reboot:**
   - Click "Save"
   - Reboot the app

### 4. Update config.yaml to Use Secrets

The app should automatically read from Streamlit secrets. If needed, you can update `config/config.yaml` to reference secrets:

```yaml
api:
  twelvedata:
    api_key: ""  # Leave empty - will be read from secrets
```

## Your Deployed App URL

After deployment, your app will be available at:
```
https://mobifom-forexanalyizer-app-[random-id].streamlit.app
```

(The exact URL will be shown after deployment completes)

## Important Security Notes

### ⚠️ Before Deploying:

1. **Remove API Key from config.yaml:**
   - Open `config/config.yaml`
   - Verify `api_key: ""` is empty
   - To `api_key: ""`
   - Commit this change

2. **Verify .gitignore:**
   - Ensure `config/users.yaml` is in .gitignore
   - Ensure `.env` files are in .gitignore

3. **Update Code to Read from Secrets:**
   - Modify your data fetcher to check Streamlit secrets first

## Reading Secrets in Your App

Add this to your `src/data/data_fetcher.py` or wherever you initialize the API:

```python
import streamlit as st

# Try to get API key from Streamlit secrets first
try:
    api_key = st.secrets["TWELVEDATA_API_KEY"]
except (KeyError, FileNotFoundError):
    # Fallback to config file
    api_key = self.config.get('api', {}).get('twelvedata', {}).get('api_key')
```

## Default Login Credentials

Your deployed app will have these default accounts:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**User Account:**
- Username: `user`
- Password: `user123`

⚠️ **IMPORTANT:** Change these passwords immediately after first login using the User Management page!

## Deployment Checklist

- [ ] Push all changes to GitHub
- [ ] Remove API key from config.yaml
- [ ] Create Streamlit Cloud account
- [ ] Deploy app with correct repository URL
- [ ] Add API key to Streamlit Secrets
- [ ] Test login with default credentials
- [ ] Change default passwords
- [ ] Test admin features (refresh data, train model)
- [ ] Test user features (limited access)
- [ ] Verify API key is working (check if real-time data is enabled)

## Troubleshooting

### App Won't Start
- Check the logs in Streamlit Cloud dashboard
- Verify all dependencies are in `requirements.txt`
- Ensure `app.py` is in the root directory

### API Key Not Working
- Verify the secret name matches exactly: `TWELVEDATA_API_KEY`
- Check that secrets are in valid TOML format
- Reboot the app after adding secrets

### Authentication Not Working
- Check that `config` directory exists
- Verify `src/auth/authentication.py` is present
- Check file paths are relative (not absolute)

### "Module Not Found" Errors
- Verify all imports use relative paths
- Check `requirements.txt` has all necessary packages
- Try clearing cache and rebooting

## Resource Limits

Streamlit Cloud free tier has these limits:
- **CPU:** Shared
- **RAM:** 1 GB
- **Storage:** Limited
- **Uptime:** App sleeps after inactivity

For production use, consider:
- Streamlit Cloud paid plans
- Self-hosting on cloud providers (AWS, GCP, Azure)
- Docker containerization

## Monitoring Your App

1. **View Logs:**
   - Go to app menu → "Manage app" → "Logs"

2. **Check Metrics:**
   - Monitor CPU and memory usage
   - Check for errors in logs

3. **User Activity:**
   - Track login attempts
   - Monitor session durations

## Updating Your App

To update your deployed app:

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push forexanalyizer main
```

Streamlit Cloud will automatically redeploy when you push to GitHub!

## Support and Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Community:** https://discuss.streamlit.io/
- **Your Repository:** https://github.com/mobifom/forexanalyizer
- **Streamlit Cloud Status:** https://streamlitstatus.com/

---

**Quick Deploy URL:** https://share.streamlit.io/deploy

**Your Repository:** https://github.com/mobifom/forexanalyizer

**Main File:** `app.py`

**Branch:** `main`

Good luck with your deployment! 🚀
