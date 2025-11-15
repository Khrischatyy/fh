# Backend Locker Downloads

This directory contains downloadable installers for the FunnyHow Device Locker application.

## Files Served

- **FunnyHow-DeviceMonitor.dmg** - macOS installer for the device locker application

## Access

Files in this directory are served via the FastAPI downloads endpoint:

- **Development**: `http://127.0.0.1/api/downloads/FunnyHow-DeviceMonitor.dmg`
- **Production**: `https://funny-how.com/api/downloads/FunnyHow-DeviceMonitor.dmg`

## Deployment

When deploying to production:

1. Build the latest DMG using the locker Makefile:
   ```bash
   cd /path/to/locker
   make dmg
   ```

2. Copy the DMG to this directory:
   ```bash
   cp locker/dist/FunnyHow-DeviceMonitor.dmg backend/locker/
   ```

3. Upload to server (files in this directory will be deployed with the backend)

## Note

The DMG file is committed to git and will be automatically deployed with the backend.
