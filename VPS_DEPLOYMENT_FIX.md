# VPS Deployment Fix Guide

## Issue Summary
The VPS is showing different CSS styling (25% width) compared to local development (17% width) for vehicle brand columns. This is because the VPS deployment may not have the latest CSS files or the static files aren't properly collected.

## Solution Steps

### Step 1: Connect to Your VPS
```bash
ssh your-username@vanparts-direct.co.uk
# or however you normally connect to your VPS
```

### Step 2: Navigate to Your Project Directory
```bash
cd /path/to/your/epc_parts_store
# Replace with your actual project path on the VPS
```

### Step 3: Pull Latest Changes from GitHub
```bash
git fetch origin
git checkout updatedversion
git pull origin updatedversion
```

### Step 4: Activate Virtual Environment (if using one)
```bash
source venv/bin/activate
# or source env/bin/activate
# depending on your virtual environment name
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 6: Restart Web Server
Choose the appropriate command based on your server setup:

**If using systemd (most common):**
```bash
sudo systemctl restart nginx
sudo systemctl restart gunicorn
# or whatever your service names are
```

**If using Apache:**
```bash
sudo systemctl restart apache2
```

**If using Docker:**
```bash
docker-compose restart
```

### Step 7: Clear Browser Cache
- Hard refresh your browser (Ctrl+F5 on Windows, Cmd+Shift+R on Mac)
- Or open the site in incognito/private mode to test

### Step 8: Verify the Fix
1. Go to https://vanparts-direct.co.uk
2. Check the vehicle navigation area
3. The vehicle brand columns should now show 17% width (6 columns per row) instead of 25% width (4 columns per row)

## Troubleshooting

### If the problem persists:

1. **Check if static files are being served correctly:**
   ```bash
   # Check if the CSS file exists on the server
   ls -la /path/to/staticfiles/css/vehicle-navigation.css
   ls -la /path/to/staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css
   ```

2. **Verify CSS content:**
   ```bash
   # Check the content of the CSS file
   head -20 /path/to/staticfiles/motortemplate/uren/assets/css/vehicle-navigation.css
   ```

3. **Check web server configuration:**
   - Ensure static files are being served correctly
   - Check nginx/apache configuration for static file serving

4. **Browser cache issues:**
   - Try accessing the site from a different device/browser
   - Use developer tools to disable cache

## Expected CSS Values

The correct CSS should show:
```css
.vehicle-brands-area .custom-category_col {
    flex: 0 0 17%;
    max-width: 17%;
    margin-bottom: 15px;
}

@media (max-width: 1599px) {
    .vehicle-brands-area .custom-category_col {
        flex: 0 0 25%;
        max-width: 25%;
    }
}
```

## Screen Size Explanation

- **Above 1600px width**: Shows 17% (6 columns)
- **Below 1600px width**: Shows 25% (4 columns)
- **Below 1200px width**: Shows 30% (3 columns)
- **Below 992px width**: Shows 35% (2-3 columns)
- **Below 768px width**: Shows 100% (1 column)

The difference you're seeing is likely because your local development screen is above 1600px wide, while the VPS is being viewed on a screen below 1600px wide.

## Files to Check

Key files that should be properly deployed:
- `epcdata/motortemplate/uren/assets/css/vehicle-navigation.css`
- `epcdata/staticfiles/css/vehicle-navigation.css`
- `epcdata/templates/oscar/storefront_base.html`

## Prevention for Future Deployments

Create a deployment script to automate this process:

```bash
#!/bin/bash
# deploy.sh
cd /path/to/your/project
git pull origin updatedversion
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
sudo systemctl restart gunicorn
echo "Deployment complete!"
```

Make it executable:
```bash
chmod +x deploy.sh
```

Then run it for future deployments:
```bash
./deploy.sh
```
