# 🚀 Step-by-Step Render Deployment Guide

## Prerequisites
- ✅ Code pushed to GitHub
- ✅ Render account (sign up at https://render.com if needed)

---

## Step 1: Create PostgreSQL Database on Render

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in or create an account

2. **Create New PostgreSQL Database**
   - Click **"New +"** button (top right)
   - Select **"PostgreSQL"**
   - Fill in the details:
     - **Name**: `civicgovgrisoft-db` (or any name you prefer)
     - **Database**: `civicgovgrisoft` (or leave default)
     - **User**: `civicgovgrisoft` (or leave default)
     - **Region**: Choose closest to you (e.g., `Oregon (US West)`)
     - **PostgreSQL Version**: Latest (default)
     - **Plan**: Free tier is fine for testing
   - Click **"Create Database"**

3. **Wait for Database to be Ready**
   - Database will provision in ~1-2 minutes
   - Status will show "Available" when ready

4. **Copy the Internal Database URL**
   - Once ready, click on your database service
   - Find **"Internal Database URL"** in the "Connections" section
   - **Copy this URL** - you'll need it in Step 3
   - Format looks like: `postgresql://user:password@hostname:5432/dbname`

---

## Step 2: Create Web Service on Render

1. **Create New Web Service**
   - Click **"New +"** button again
   - Select **"Web Service"**
   - Connect your GitHub account if not already connected
   - Select your repository: `CivicGovGrisoft` (or your repo name)

2. **Configure Basic Settings**
   - **Name**: `civicgovgrisoft` (or your preferred name)
   - **Region**: Same region as your database
   - **Branch**: `main` (or `master` - your default branch)
   - **Root Directory**: Leave empty (unless your Django project is in a subdirectory)
   - **Runtime**: `Python 3`
   - **Python Version**: `3.11.9` (or latest 3.11.x)

---

## Step 3: Configure Build & Start Commands

In the Web Service settings, configure:

### Build Command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### Start Command:
```bash
gunicorn civic_project.wsgi
```

**Copy and paste these exactly as shown above.**

---

## Step 4: Set Environment Variables

Click on **"Advanced"** → **"Environment Variables"** and add:

1. **SECRET_KEY**
   - Key: `SECRET_KEY`
   - Value: Generate a strong secret key (you can use: https://djecrety.ir/ or run: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - Example: `django-insecure-xyz123abc456...` (long random string)

2. **DEBUG**
   - Key: `DEBUG`
   - Value: `False`

3. **ALLOWED_HOSTS**
   - Key: `ALLOWED_HOSTS`
   - Value: `your-app-name.onrender.com` (Replace `your-app-name` with your actual web service name)
   - Example: If your service is named `civicgovgrisoft`, use: `civicgovgrisoft.onrender.com`

4. **DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: Paste the **Internal Database URL** you copied in Step 1
   - Should look like: `postgresql://user:password@hostname:5432/dbname`

### Environment Variables Summary:
```
SECRET_KEY = <your-generated-secret-key>
DEBUG = False
ALLOWED_HOSTS = your-app-name.onrender.com
DATABASE_URL = <internal-database-url-from-step-1>
```

---

## Step 5: Deploy

1. **Review Settings**
   - Double-check all environment variables are set
   - Verify build and start commands are correct

2. **Click "Create Web Service"**
   - Render will start building your application
   - This will take 5-10 minutes on first build

3. **Monitor the Build Logs**
   - Watch the build logs for any errors
   - You should see:
     - ✅ Installing dependencies
     - ✅ Collecting static files
     - ✅ Build completed successfully

---

## Step 6: Run Database Migrations

**IMPORTANT**: Migrations are NOT run automatically. You must run them manually.

### After your first deployment succeeds:

1. **Open Render Shell**
   - In your Web Service dashboard, click on **"Shell"** tab (or look for terminal icon)
   - This opens a command-line interface

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```
   - Wait for migrations to complete
   - You should see: "Applying core.0001_initial... OK"

3. **Create Superuser (Optional but Recommended)**
   ```bash
   python manage.py createsuperuser
   ```
   - Enter username, email, and password when prompted
   - This creates an admin user for Django admin panel

---

## Step 7: Access Your Application

1. **Get Your App URL**
   - After deployment, Render provides a URL
   - Format: `https://your-app-name.onrender.com`
   - It's shown at the top of your Web Service dashboard

2. **Visit the URL**
   - Open in browser
   - You should see your application's login/auth page

3. **Access Admin Panel (if you created superuser)**
   - Go to: `https://your-app-name.onrender.com/admin`
   - Log in with superuser credentials

---

## ✅ Troubleshooting

### Build Fails with "Module not found"
- Check `requirements.txt` has all dependencies
- Verify Python version is correct (3.11.9)

### "Application Error" when visiting URL
- Check service logs (click "Logs" tab)
- Common issues:
  - Migrations not run → Run `python manage.py migrate` in Shell
  - Wrong DATABASE_URL → Verify Internal Database URL is correct
  - Missing environment variables → Check all env vars are set

### "DisallowedHost" Error
- Check ALLOWED_HOSTS includes your Render URL
- Should be: `your-app-name.onrender.com`

### Database Connection Errors
- Verify DATABASE_URL uses **Internal Database URL** (not External)
- Ensure database service is running
- Check environment variable name is exactly `DATABASE_URL`

### Static Files Not Loading
- Verify `collectstatic` is in build command
- Check WhiteNoise is in MIDDLEWARE (already configured)
- Check STATIC_ROOT setting

---

## 🎉 Success Checklist

- [ ] PostgreSQL database created and running
- [ ] Web service created and connected to GitHub
- [ ] Build command configured
- [ ] Start command configured
- [ ] All environment variables set (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL)
- [ ] First deployment completed successfully
- [ ] Migrations run via Shell
- [ ] Superuser created (optional)
- [ ] Application accessible via URL
- [ ] Admin panel accessible (if superuser created)

---

## 📝 Notes

- **Free Tier Limitations**: 
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down takes ~30 seconds
  - Consider upgrading for production use

- **Media Files**: 
  - Render's filesystem is ephemeral (files are lost on restart)
  - For production, use external storage (AWS S3, Cloudinary, etc.)

- **Environment Variables**:
  - Can be updated anytime in the dashboard
  - Changes require a redeploy (automatic)

- **Database Backups**:
  - Free tier doesn't include automatic backups
  - Consider manual backups for important data

---

## Need Help?

If you encounter any issues:
1. Check the build logs and runtime logs
2. Verify all environment variables are correct
3. Ensure migrations are run
4. Check Render status page: https://status.render.com

Good luck with your deployment! 🚀

