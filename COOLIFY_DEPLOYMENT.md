# Coolify Deployment Guide

## Latest Error Resolution

The new error you encountered:
```
failed to solve: process "/bin/sh -c echo "=== Listing files ===" && ls -la && echo "=== Contents of requirements.txt ===" && cat requirements.txt && echo "=== Installing Python packages ===" && pip3 install --no-cache-dir -r requirements.txt" did not complete successfully: exit code: 1
```

This indicates that the pip install process is failing during the Docker build.

## Quick Solutions (Try in Order)

### Solution 1: Use Minimal Dockerfile (Fastest)

1. **In Coolify, set Dockerfile to**: `Dockerfile.minimal`
2. **Use Docker Compose file**: `docker-compose.coolify.yml`

This version:
- Uses Python 3.11 slim base image
- Only installs Flask (no security tools initially)
- Has graceful fallbacks for missing tools
- Much faster build time

### Solution 2: Use Updated Requirements

The requirements.txt has been updated with more stable versions:
```
Flask==2.3.3
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.3
```

### Solution 3: Test with Minimal Requirements

If still failing, use `requirements.minimal.txt`:
```
Flask==2.3.3
Werkzeug==2.3.7
```

## Coolify Configuration Steps

### Step 1: Choose Dockerfile
In your Coolify project settings:
- **Dockerfile**: `Dockerfile.minimal`
- **Docker Compose**: `docker-compose.coolify.yml`

### Step 2: Environment Variables
Set these in Coolify:
```
FLASK_ENV=production
FLASK_DEBUG=0
PYTHONUNBUFFERED=1
```

### Step 3: Port Configuration
- **Internal Port**: `5000`
- **External Port**: `80` or `443`

## What's Different in Minimal Version

### Features Available:
✅ Web interface works  
✅ Domain input and validation  
✅ Scan progress tracking  
✅ Report generation  
✅ Mock data for demonstration  

### Features with Fallbacks:
🔄 Subdomain enumeration (uses mock data if tools unavailable)  
🔄 Port scanning (uses mock data if tools unavailable)  
🔄 Vulnerability scanning (uses mock data if tools unavailable)  

### Build Process:
1. Python 3.11 slim base
2. Install curl for health checks
3. Install Flask dependencies
4. Copy application files
5. Ready to run

## Testing Locally

Test the minimal version locally:

```bash
# Build minimal version
docker build -f Dockerfile.minimal -t scanner-minimal .

# Run it
docker run -p 5000:5000 scanner-minimal

# Test in browser
curl http://localhost:5000
```

## Upgrade Path

Once the minimal version is working in Coolify:

1. **Phase 1**: Deploy minimal version (Flask only)
2. **Phase 2**: Add Go and security tools later
3. **Phase 3**: Enable full scanning capabilities

## Alternative: Manual Requirements Test

If you want to debug the requirements issue:

```bash
# Test requirements locally
docker run --rm -v $(pwd):/app python:3.11-slim sh -c "cd /app && pip install -r requirements.txt"
```

## Files to Use for Coolify

**Primary files for Coolify deployment:**
- `Dockerfile.minimal` - Simplified Docker build
- `docker-compose.coolify.yml` - Coolify-optimized compose
- `requirements.txt` - Updated with stable versions
- `app.py` - Updated with tool fallbacks

## Expected Build Time

- **Minimal version**: 2-3 minutes
- **Full version**: 8-12 minutes (due to Go and security tools)

## Next Steps

1. **Try Dockerfile.minimal first** - This should work immediately
2. **Verify the web interface loads** - Check http://your-domain:5000
3. **Test a scan** - It will use mock data but show the interface works
4. **Upgrade to full version later** - Once basic deployment works

The minimal version will get you up and running quickly, then you can add the security tools in a second phase.