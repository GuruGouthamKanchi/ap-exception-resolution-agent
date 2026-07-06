# Deploying FastAPI Backend to Render

This guide outlines the steps to deploy the Python FastAPI backend service to **Render** utilizing the Blueprint specification in [render.yaml](file:///d:/kaggle/backend/render.yaml).

## 🚀 Deployment Steps

### 1. Push Code to GitHub
Render deploys continuously from your connected GitHub repository. 
If you have made code modifications, push them to GitHub:
```bash
git add .
git commit -m "chore: support env credential string and blueprint render.yaml"
git push origin main
```

---

### 2. Configure Web Service on Render

1. Log in to your **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** in the top right corner and select **Web Service**.
3. Select your connected GitHub account and connect the `ap-exception-resolution-agent` repository.
4. Set the following properties in the creation wizard:
   * **Name**: `ap-exception-backend`
   * **Region**: Choose the region closest to you or your database.
   * **Branch**: `main`
   * **Root Directory**: `backend` (This is critical because the repo contains both `frontend/` and `backend/` directories).
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   * **Instance Type**: Select the **Free** tier.

---

### 3. Configure Environment Variables

Navigate to the **Environment** tab of your Web Service in Render and add the following keys:

| Key | Description / Value |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key. |
| `FIREBASE_CREDENTIALS_JSON` | Copy and paste the **entire contents** of your `firebase-credentials.json` file as a single-line string here. |

> [!IMPORTANT]
> The codebase automatically prioritizes `FIREBASE_CREDENTIALS_JSON` (the string) over local file paths on Render, ensuring credentials remain secure and are not committed to the repo.

---

### 4. Locate Deployed URL
Once the service build succeeds, you will find your live URL in the top left header of your Web Service dashboard:
`https://ap-exception-backend.onrender.com`

Confirm the backend works by visiting:
`https://ap-exception-backend.onrender.com/health`

---

## 🔄 Auto-Deploy and Manual Redeployment
Render automatically deploys on every push to your connected `main` branch on GitHub. 
If auto-deploy is turned off in your settings, you can trigger a deployment manually:
1. Go to your Web Service page in the **Render Dashboard**.
2. Click the **Manual Deploy** dropdown in the top right.
3. Select **Clear Build Cache & Deploy**.

---

## 🔍 Deployed Smoke-Test Checklist

Follow these verification checks to confirm the live cloud system is operational:

1. **Verify Backend Health**:
   * Navigate directly to: `https://ap-exception-resolution-agent.onrender.com/health` (or your active service URL).
   * Confirm that it returns: `{"status": "ok"}`.
   * *Note*: If the page spins, wait 30-60 seconds for Render's container to cold-start.

2. **Verify CORS Connection**:
   * Load the deployed Vercel frontend URL: `https://ap-exception-resolution-agent.vercel.app/`.
   * Confirm the dashboard cards and lists load without any `"Connection Failed"` overlays or CORS errors in your browser console (F12).

3. **Verify DB Data Loading**:
   * Confirm the dashboard metrics show non-zero numbers representing the seeded 30 Purchase Orders and resolutions.

4. **Verify E2E Processing Pipeline**:
   * Go to the **Process Invoice** tab in your Vercel frontend.
   * Click **Select Sample** -> choose **INV-5001 (Clean Match)** or **INV-5026 (Major Mismatch)**.
   * Click **Process Invoice** and verify that all stages complete successfully and the corresponding discrepancy/reasoning panels are populated.

5. **Verify Live Render Logs**:
   * Navigate to the **Logs** tab of your service in the Render Dashboard during your processing run.
   * Confirm that incoming POST requests to `/process-invoice` are logged with status code `200` or `201` without swallowing exceptions.

---

## ⚠️ Render Free Tier Warm-up Gotcha

> [!WARNING]
> Render's **Free Tier** web services automatically spin down (suspend) after **15 minutes** of inactivity.
> 
> When suspended, the next request will trigger a **cold-start**, which takes **30 to 60 seconds** to provision and boot the server container. During your live demo, a slow first request might be mistaken for a bug. 
> 
> **Recommendation**: Hit the `/health` endpoint of your deployed service a minute or two before starting your demo to warm the server container up!

