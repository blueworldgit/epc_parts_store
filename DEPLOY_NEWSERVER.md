# New Server Deployment Guide

## Quick Deployment Steps

### 1. On Your Development Machine
```bash
git checkout -b new-server-deployment
# Make any server-specific changes
git add .
git commit -m "Add new server deployment configuration"
git push origin new-server-deployment
```

### 2. On the New Server
```bash
# Clone the repository
git clone https://github.com/blueworldgit/epc_parts_store.git
cd epc_parts_store

# Switch to the new server branch
git checkout new-server-deployment

# Run the deployment script
chmod +x deploy_newserver.sh
./deploy_newserver.sh
```

### 3. Manual Configuration Steps

#### Update Environment File
Edit `.env.newserver`:
- Server IP is already set to: 80.95.207.45
- Database is configured: vanrentalsnewdb on 80.95.207.42
- Replace `new-domain.com` with your actual domain
- Database credentials are already set (epc_user/N0rfolk)
- Generate new SECRET_KEY

#### Update Nginx Configuration
Edit `newserver.conf`:
- Replace `NEW_DOMAIN.com` with your actual domain
- Replace `USERNAME` with your server username
- Update file paths as needed

#### Setup SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Start the Application
```bash
source env/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 4. Production Process Management (Optional)
Consider using Gunicorn + systemd for production:

```bash
pip install gunicorn
sudo nano /etc/systemd/system/epc-parts.service
```

## Environment Detection Logic

The Django settings will automatically detect the new server environment based on:
1. DJANGO_ENV=production in environment file
2. Server IP detection (if configured)
3. Hostname detection
4. .prod file existence

## Files Created for New Server:
- `.env.newserver` - Environment variables template
- `newserver.conf` - Nginx configuration template  
- `deploy_newserver.sh` - Automated deployment script
- `DEPLOY_NEWSERVER.md` - This guide