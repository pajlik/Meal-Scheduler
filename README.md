# 🍽️ Cook WhatsApp Notifier

Automatically sends your cook a WhatsApp message every morning with the day's meal plan — pulled from Google Sheets, sent via Green API (WhatsApp), hosted on GCP Cloud Run.

---

## 📁 Project Structure

```
cook-whatsapp/
├── src/
│   ├── main.py          # Flask app — Cloud Run entry point
│   ├── sheets.py        # Reads meal plan from Google Sheets
│   └── whatsapp.py      # Sends WhatsApp message via Green API
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🗂️ Step 1 — Set Up Google Sheet

Create a Google Sheet with this structure:

| Date (DD/MM/YYYY) | Breakfast | Lunch | Dinner | Snacks |
|---|---|---|---|---|
| 30/03/2026 | Poha, Chai | Dal Rice Roti | Khichdi | Samosa |
| 31/03/2026 | Idli Sambhar | Rajma Chawal | Roti Sabzi | |

- Row 1 = Header (skipped automatically)
- Date format must be `DD/MM/YYYY`
- Snacks column is optional

---

## 🔑 Step 2 — Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **Google Sheets API**
4. Go to **IAM & Admin → Service Accounts → Create Service Account**
5. Download the JSON key file → save as `service-account.json`
6. **Share your Google Sheet** with the service account email (viewer access)
7. Copy your **Sheet ID** from the URL:
   `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`

---

## 📱 Step 3 — Green API Setup

1. Sign up at [green-api.com](https://green-api.com/)
2. Create a new instance from the dashboard
3. Scan the QR code with your WhatsApp (the number that will send messages)
4. Note down:
   - `Instance ID` (e.g. `7107569687`)
   - `API Token`
   - `API URL` shown in your instance settings (e.g. `https://7107.api.greenapi.com`)

> Free tier allows 500 messages/month — more than enough for daily cook notifications.

---

## ☁️ Step 4 — Deploy to GCP Cloud Run

### Prerequisites
```bash
# Install Google Cloud SDK
brew install google-cloud-sdk   # macOS
# or follow: https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Build & Deploy
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
gcloud run deploy cook-notifier \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_SHEET_ID=your_sheet_id,GREEN_API_INSTANCE_ID=your_instance_id,GREEN_API_TOKEN=your_token,GREEN_API_BASE_URL=https://XXXX.api.greenapi.com,COOK_WHATSAPP_NUMBER=91XXXXXXXXXX,GOOGLE_SERVICE_ACCOUNT_JSON=/app/service-account.json"
```

> ⚠️ For the service account JSON, either mount it as a secret or use **GCP Secret Manager** (recommended).

### Using Secret Manager (recommended):
```bash
# Store secrets
gcloud secrets create service-account-json --data-file=service-account.json

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding service-account-json \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

---

## ⏰ Step 5 — Set Up Daily Trigger (Cloud Scheduler)

```bash
# Enable Cloud Scheduler
gcloud services enable cloudscheduler.googleapis.com

# Create a daily job at 7:00 AM IST (UTC+5:30 = 1:30 AM UTC)
gcloud scheduler jobs create http cook-daily-message \
  --schedule="30 1 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/send" \
  --http-method=POST \
  --location=asia-south1
```

---

## 🧪 Step 6 — Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill env vars
cp .env.example .env
# edit .env with your values

# Run locally
cd src
python main.py

# In another terminal, trigger the send
curl http://localhost:8080/send
```

---

## 📲 What the Message Looks Like

```
🍽️ *आज का मेनू — 30/03/2026*

🌅 *नाश्ता (Breakfast):*
Poha, Chai

☀️ *दोपहर का खाना (Lunch):*
Dal, Rice, Sabzi, Roti

🌙 *रात का खाना (Dinner):*
Khichdi, Papad

☕ *स्नैक्स (Snacks):*
Samosa

धन्यवाद! 🙏
```

---

## 🔧 Customization

- **Change language**: Edit `build_message()` in `whatsapp.py`
- **Change time**: Update the cron schedule in Cloud Scheduler
- **Add more meal types**: Add columns to your sheet and update `sheets.py`
- **Multiple cooks**: Call `send_whatsapp_message()` with different numbers

---

## 🆘 Troubleshooting

| Issue | Fix |
|---|---|
| `No entry found for today` | Check date format in sheet is `DD/MM/YYYY` |
| `401 from Green API` | Token incorrect — check `GREEN_API_TOKEN` in dashboard |
| `403 from Sheets API` | Sheet not shared with service account email |
| Message not received | Check instance is connected (QR scanned & active) in Green API dashboard |
| Instance disconnected | Re-scan QR code in Green API dashboard |
