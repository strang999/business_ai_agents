# � Skylix WhatsApp Bot - Production Deployment Guide

This guide is for deploying the bot to a status where clients can test it 24/7.

## 🔑 Part 1: Permanent Meta Token Setup (CRITICAL)

The "Temporary Access Token" you see in the dashboard expires in 24 hours. **Do not use it for client demos.**

### Steps to get a Permanent Token:

1.  **Go to Business Settings**:
    *   Navigate to [business.facebook.com/settings](https://business.facebook.com/settings).
    *   Select your Business Portfolio associated with the app.

2.  **Create a System User**:
    *   In the left sidebar, go to **Users** -> **System Users**.
    *   Click **Add**.
    *   Name: `SkylixBotUser`.
    *   Role: **employee**.
    *   Click **Create System User**.

3.  **Add Assets**:
    *   Select the newly created user (`SkylixBotUser`).
    *   Click **Add Assets**.
    *   Select **Apps** -> Choose your App (`SkylixRealEstateBot`).
    *   Toggle **Manage App** (Full Control) -> Save Changes.

4.  **Generate Token**:
    *   With the user still selected, click **Generate New Token**.
    *   **Select App**: Choose your app.
    *   **Token Expiration**: Select **Never** (or Permanent).
    *   **Permissions**: YOU MUST CHECK THESE:
        *   `whatsapp_business_messaging`
        *   `whatsapp_business_management`
    *   Click **Generate Token**.

5.  **Save Token**:
    *   Copy this long string. This is your **Permanent `META_ACCESS_TOKEN`**.
    *   Update your `.env` file (or deployment secrets) with this token.

---

## ☁️ Part 2: Deploying to the Cloud (Free/Cheap)

To keep the bot running 24/7 without your laptop, we recommend **Render** or **Railway**. Both have free/cheap tiers perfect for demos.

### Option A: Deploy on Render (Recommended)

1.  **Push Code to GitHub**:
    *   Ensure this folder `skylix_portfolio` is in a GitHub repository.

2.  **Create Service on Render**:
    *   Go to [dashboard.render.com](https://dashboard.render.com/).
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub repository.

3.  **Configure Settings**:
    *   **Root Directory**: `skylix_portfolio/real_estate` (Important! This tells Render where the app is).
    *   **Runtime**: Python 3.
    *   **Build Command**: `pip install -r requirements.txt`.
    *   **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`.

4.  **Environment Variables**:
    *   Scroll down to **Environment Variables**.
    *   Add all keys from your `.env` file:
        *   `OPENAI_API_KEY`
        *   `FIRECRAWL_API_KEY`
        *   `META_ACCESS_TOKEN` (The Permanent one from Part 1)
        *   `META_PHONE_NUMBER_ID`
        *   `META_VERIFY_TOKEN` (e.g., `skylix_secure_123`)

5.  **Deploy**:
    *   Click **Create Web Service**.
    *   Wait for it to build. Once live, Render will give you a **URL** (e.g., `https://skylix-bot.onrender.com`).

---

## 🔗 Part 3: Connecting Meta to Cloud

1.  Copy your new **Render URL**.
2.  Go to [developers.facebook.com](https://developers.facebook.com/).
3.  Go to **WhatsApp** -> **Configuration**.
4.  **Edit Webhook**:
    *   **Callback URL**: `https://skylix-bot.onrender.com/webhook` (Append `/webhook`!).
    *   **Verify Token**: Enter your `META_VERIFY_TOKEN`.
5.  Click **Verify and Save**.

✅ **DONE!** Your bot is now live 24/7. You can send the WhatsApp number to clients for testing.

---

## 🛠️ Part 4: Testing (Prod)

1.  Open WhatsApp on your phone.
2.  Message the bot number: "Hi" or "I want to buy a flat in Bangalore".
3.  Watch the logs in your Render Dashboard to see the server working.

**Note on Database**:
Currently, the bot uses a `json` file (`real_estate_leads.json`) for memory. on platforms like Render (Free Tier), this file **will verify reset** every time the server restarts.
*   **For Demos**: This is usually fine.
*   **For Long Term**: You need a real database (Postgres/Firebase). If you need this upgrade, ask me!
