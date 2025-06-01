# Coolify Deployment Guide

## Issue Resolution

The error you encountered:
```
failed to solve: failed to compute cache key: failed to calculate checksum of ref 9bc2aee7-ae90-4fee-9644-d6c8aad1e6da::not2r06t84jghqcuc9dsnzt9i: "/requirements.txt": not found
```

This typically happens when Coolify can't find the `requirements.txt` file during the Docker build process.

## Solutions

### Option 1: Use the Simple Dockerfile (Recommended for Coolify)

1. In your Coolify project settings, specify the Dockerfile:
   ```
   Dockerfile: Dockerfile.simple
   ```

2. Or rename the simple Dockerfile:
   ```bash
   mv Dockerfile.simple Dockerfile
   ```

### Option 2: Use Coolify-specific Docker Compose

1. In Coolify, use the `coolify-docker-compose.yml` file instead of the default one
2. This file is specifically configured for Coolify compatibility

### Option 3: Manual File Verification

1. Ensure all files are properly committed to your Git repository
2. Check that `requirements.txt` is in the root directory
3. Verify the `.dockerignore` file isn't excluding `requirements.txt`

## Coolify Configuration

### Environment Variables
Set these in your Coolify project:
- `FLASK_ENV=production`
- `FLASK_DEBUG=0`
- `PYTHONUNBUFFERED=1`

### Port Configuration
- Internal Port: `5000`
- External Port: `80` or `443` (as configured in Coolify)

### Volume Mounts
- Mount `/tmp/scans` for temporary scan data storage

## Build Process

The simplified Dockerfile (`Dockerfile.simple`) includes:
1. Python 3.11 base image
2. System dependencies installation
3. Go installation for security tools
4. Security tools installation (Subfinder, Naabu, Nuclei)
5. Application setup

## Troubleshooting Steps

1. **Check File Existence**:
   ```bash
   ls -la requirements.txt
   cat requirements.txt
   ```

2. **Verify Git Repository**:
   - Ensure all files are committed
   - Check `.gitignore` doesn't exclude required files

3. **Use Simple Build**:
   - Try the `Dockerfile.simple` which has fewer layers
   - This reduces complexity and potential build issues

4. **Check Coolify Logs**:
   - Review build logs in Coolify dashboard
   - Look for specific error messages

## Alternative Deployment Methods

If Coolify continues to have issues, you can:

1. **Use Docker Hub**:
   - Build locally and push to Docker Hub
   - Deploy from Docker Hub in Coolify

2. **Use GitHub Actions**:
   - Set up CI/CD to build and deploy automatically

3. **Manual Docker Build**:
   ```bash
   docker build -f Dockerfile.simple -t attack-surface-scanner .
   docker run -p 5000:5000 attack-surface-scanner
   ```

## File Structure Verification

Ensure your project has this structure:
```
project/
├── app.py
├── requirements.txt
├── Dockerfile.simple
├── coolify-docker-compose.yml
├── templates/
│   └── index.html
├── config.py
└── .dockerignore
```

## Contact

If you continue to experience issues, the problem might be:
1. Coolify-specific configuration
2. Git repository synchronization
3. File permissions

Try using the `Dockerfile.simple` first, as it's designed to be more compatible with various deployment platforms including Coolify.