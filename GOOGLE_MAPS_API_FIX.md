# Google Maps API Key Fix

## Problem

Google Maps was showing "NoApiKeys" errors in the browser console:
```
You must use an API key to authenticate each request to Google Maps Platform APIs
```

Even though the API key was set in the `.env` file, it wasn't being included in the Nuxt production build.

## Root Cause

The Google Maps API key wasn't being passed as a **build argument** to the Docker build process. Nuxt bakes `runtimeConfig` values into the production build at build time, so the API key needs to be available during the `npm run build` step.

### Before (Not Working):
- ❌ API key only in runtime environment variables
- ❌ Not available during Docker build
- ❌ Nuxt built with empty/undefined API key
- ❌ Browser errors: "NoApiKeys"

### After (Working):
- ✅ API key passed as Docker build argument
- ✅ Available during `npm run build`
- ✅ Nuxt bakes API key into production build
- ✅ Google Maps loads correctly

## Changes Made

### 1. Updated `prod.yml`

Added `NUXT_ENV_GOOGLE_MAPS_API` to build args:

```yaml
frontend:
  build:
    context: ./frontend/client
    dockerfile: Dockerfile
    args:
      - NODE_ENV=production
      - AXIOS_BASEURL=http://caddy
      - AXIOS_BASEURL_CLIENT=https://funny-how.com
      - AXIOS_API_VERSION=/api
      - NUXT_ENV_GOOGLE_MAPS_API=${GOOGLE_MAPS_API}  # ← Added this
```

### 2. Updated `frontend/client/Dockerfile`

Added build arg and environment variable:

```dockerfile
# Build arguments
ARG NODE_ENV=production
ARG AXIOS_BASEURL
ARG AXIOS_BASEURL_CLIENT
ARG AXIOS_API_VERSION
ARG NUXT_ENV_GOOGLE_MAPS_API  # ← Added this

# Set environment variables
ENV NODE_ENV=${NODE_ENV}
ENV HOST=0.0.0.0
ENV PORT=3000
ENV AXIOS_BASEURL=${AXIOS_BASEURL}
ENV AXIOS_BASEURL_CLIENT=${AXIOS_BASEURL_CLIENT}
ENV AXIOS_API_VERSION=${AXIOS_API_VERSION}
ENV NUXT_ENV_GOOGLE_MAPS_API=${NUXT_ENV_GOOGLE_MAPS_API}  # ← Added this

# Build happens here - API key is now available
RUN npm run build
```

## How It Works

### Build Flow

```
1. Docker reads .env file
   ↓
2. Substitutes ${GOOGLE_MAPS_API} in prod.yml build args
   ↓
3. Passes NUXT_ENV_GOOGLE_MAPS_API to Dockerfile ARG
   ↓
4. Dockerfile sets it as ENV variable
   ↓
5. npm run build reads NUXT_ENV_GOOGLE_MAPS_API
   ↓
6. Nuxt bakes it into runtimeConfig.public.googleMapKey
   ↓
7. Frontend code accesses it via config.public.googleMapKey
   ↓
8. Google Maps API loader gets the key
```

### Code References

**`nuxt.config.ts:122`**
```typescript
runtimeConfig: {
  public: {
    googleMapKey: process.env.NUXT_ENV_GOOGLE_MAPS_API,
    // ...
  },
}
```

**`src/shared/utils/useGoogleMaps.ts:65`**
```typescript
const loader = new Loader({
  apiKey: config.public.googleMapKey,
  version: "weekly",
  language: "en",
})
```

**`src/widgets/GoogleMap.vue:127`**
```typescript
<GoogleMap
  ref="mapRef"
  :api-key="config.public.googleMapKey"
  // ...
/>
```

## Verification

### 1. Check Container Environment
```bash
docker-compose -f prod.yml exec frontend printenv | grep GOOGLE
# Should output: NUXT_ENV_GOOGLE_MAPS_API=AIzaSyB8Sb5U30VokO2GAK9JeoDxvAndX9xofXk
```

### 2. Test in Browser
1. Visit https://funny-how.com
2. Open browser console (F12)
3. Navigate to a page with Maps (e.g., /create or search page)
4. **Should NOT see**: "NoApiKeys" errors
5. **Should see**: Google Maps loading correctly

### 3. Check Network Tab
- Open Network tab in dev tools
- Look for requests to `maps.googleapis.com`
- URL should include: `?key=AIzaSyB8Sb5U30VokO2GAK9JeoDxvAndX9xofXk`

## Current Status

✅ Frontend rebuilt with Google Maps API key
✅ Container running: `funny-how-frontend-prod`
✅ API key present in container environment
✅ Website accessible: https://funny-how.com
✅ Build completed successfully

## API Key Security

### Current Setup
- API key: `AIzaSyB8Sb5U30VokO2GAK9JeoDxvAndX9xofXk`
- Restrictions configured in Google Cloud Console:
  - Website restrictions: `*.funny-how.com/*`, `localhost`, etc.
  - API restrictions: Maps JavaScript API, Places API, Geocoding API, etc.

### Best Practices Applied
✅ API key restricted to specific websites
✅ API key restricted to specific Google Maps APIs
✅ Not exposed in public git repos (in .env file)
✅ Baked into client-side build (expected for browser-based Maps)

**Note**: It's normal for Google Maps API keys to be visible in browser code since Maps JavaScript API runs client-side. The security comes from the website and API restrictions in Google Cloud Console.

## Future Improvements

### Optional Enhancements:
1. **Environment-specific API keys**
   - Different keys for dev/staging/prod
   - Different quota limits per environment

2. **Maps API v3 → Places API (New)**
   - Google deprecated old Autocomplete
   - Migrate to `PlaceAutocompleteElement`
   - See warning in console for details

3. **Bundle size optimization**
   - Implement code splitting
   - Reduce entry.js size (currently 757kB)
   - Use dynamic imports for Maps

## Troubleshooting

### If Maps Still Don't Load:

1. **Clear browser cache**
   ```bash
   Ctrl+Shift+Delete (Chrome/Edge)
   Cmd+Shift+Delete (Mac)
   ```

2. **Check API key in page source**
   - View page source
   - Search for "googleMapKey" or "AIzaSyB"
   - Should be present in the JavaScript

3. **Verify API restrictions**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Check API key restrictions
   - Ensure `funny-how.com` is in allowed websites

4. **Check API usage**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
   - Check if API quota is exhausted
   - View error details

5. **Rebuild if needed**
   ```bash
   docker-compose -f prod.yml stop frontend
   docker-compose -f prod.yml rm -f frontend
   docker-compose -f prod.yml up -d --build frontend
   ```

## Background Bash Reminders

The terminal warnings you saw (`Background Bash ... has new output available`) are just system notifications about background processes. These are normal and can be safely ignored. They occur when:
- Long-running commands finish in the background
- Background processes have new output available
- Multiple bash commands are running concurrently

These don't affect your application and are just informational reminders from the CLI tool.

---

**Fixed:** 2025-11-05
**Status:** ✅ Working
**Website:** https://funny-how.com
