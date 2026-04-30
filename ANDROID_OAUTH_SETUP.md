# Android OAuth Setup

## The Problem

Google OAuth on Android doesn't work with localhost or private IPs. iOS can use `localhost:8000` directly, but Android needs a public HTTPS URL. We use ngrok to create a tunnel to the local backend.

## How It Works

iOS just uses `http://localhost:8000/api/v1/auth/providers/google/callback` and it works fine.

For Android, Google redirects to an ngrok URL (like `https://abc123.ngrok-free.dev/api/v1/auth/providers/google/callback`), ngrok forwards that to your backend at localhost:8000, then your backend processes it and redirects back to the app.

## Setup Steps

### 1. Install ngrok

```bash
brew install ngrok
```

Sign up at https://dashboard.ngrok.com/signup for the free account, then get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken and run:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### 2. Start ngrok

Run this and keep the terminal open:

```bash
ngrok http 8000
```

You'll see an HTTPS URL in the output, something like `https://abc123.ngrok-free.dev`. You can also check http://localhost:4040 to see the web interface.

### 3. Add Redirect URI to Google Cloud Console

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Click on your Web OAuth Client ID (same one used for iOS)
3. Under Authorized redirect URIs, click + ADD URI
4. Add: `https://YOUR_NGROK_URL/api/v1/auth/providers/google/callback`
   - Replace YOUR_NGROK_URL with the actual URL from step 2
   - Example: `https://abc123.ngrok-free.dev/api/v1/auth/providers/google/callback`
5. Click SAVE

Make sure you also have `http://localhost:8000/api/v1/auth/providers/google/callback` in there for iOS.

### 4. Create .env File

Create a `.env` file in `frontend/Vellora/`:

```bash
cd Vellora/frontend/Vellora
touch .env
```

Add this line (replace with your actual ngrok URL):

```
EXPO_PUBLIC_ANDROID_REDIRECT_URI=https://YOUR_NGROK_URL/api/v1/auth/providers/google/callback
```

No quotes, no spaces. Example:

```
EXPO_PUBLIC_ANDROID_REDIRECT_URI=https://abc123.ngrok-free.dev/api/v1/auth/providers/google/callback
```

### 5. Restart Expo

Stop Expo (Ctrl+C) and restart with cleared cache:

```bash
npx expo start --clear
```

Expo only reads environment variables when it starts, so you need to fully restart, not just reload the app.

### 6. Test

Make sure:

- Backend is running on localhost:8000
- ngrok is running
- Redirect URI is in Google Cloud Console
- .env file exists with the right URL
- Expo has been restarted

Then try Google OAuth on Android.

## Notes

Each person needs their own ngrok URL and has to add it to Google Cloud Console once. The URL changes every time you restart ngrok (free tier), so try to keep it running. If you do restart ngrok, you'll need to update Google Cloud Console and your .env file with the new URL, then restart Expo.

If you close your laptop, ngrok stops. When you start it again, you'll get a new URL and need to update everything.

## Common Issues

**redirect_uri_mismatch error:**

- The redirect URI in your .env must exactly match what's in Google Cloud Console
- Make sure you restarted Expo (not just reloaded)
- Check that .env is in frontend/Vellora/ directory

**Environment variable not loading:**

- Must be in frontend/Vellora/ directory
- Variable name must start with EXPO*PUBLIC*
- Must fully restart Expo

**ngrok not working:**

- Make sure you added the authtoken
- Make sure backend is running on port 8000
- Check http://localhost:4040 for ngrok status

## Current Setup

- iOS: `http://localhost:8000/api/v1/auth/providers/google/callback`
- Android: Uses ngrok URL from EXPO_PUBLIC_ANDROID_REDIRECT_URI in .env
- Backend: Single Web OAuth Client ID for both platforms
- Google Cloud Console: Has both localhost,iOS and ngrok URLs

## PDF Downloads on Android ONLY

PDF downloads from LocalStack S3 also need ngrok on Android. You'll need to switch ngrok between port 8000 (for OAuth) and port 4566 (for PDFs generation).

### For PDF Downloads

Run ngrok on port 4566:

```bash
ngrok http 4566
```

Add to your `.env` file:

```
EXPO_PUBLIC_LOCALSTACK_URL=https://YOUR_NGROK_URL
```

**Note:** With ngrok free tier you only can run one tunnel at a time. Switch between:

- Port 8000 for OAuth: `ngrok http 8000`
- Port 4566 for PDFs: `ngrok http 4566`

The ngrok URL stays the same when you switch ports, so you can use the same URL in your `.env` for both.
