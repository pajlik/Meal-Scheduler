import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify
from sheets import get_todays_meals, get_all_rows
from whatsapp import send_whatsapp_message

app = Flask(__name__)


@app.route("/send", methods=["GET", "POST"])
def send():
    """
    Endpoint triggered by GCP Cloud Scheduler every morning.
    Fetches today's meal plan and sends it via WhatsApp.
    """
    print("📋 Fetching today's meal plan from Google Sheets...")
    meals = get_todays_meals()

    if not meals:
        msg = "⚠️ No meal plan found for today. Please update the Google Sheet."
        print(msg)
        return jsonify({"status": "skipped", "reason": msg}), 200

    print(f"✅ Meals found: {meals}")
    print("📲 Sending WhatsApp message to cook...")

    success = send_whatsapp_message(meals)

    if success:
        return jsonify({"status": "sent", "meals": meals}), 200
    else:
        return jsonify({"status": "failed"}), 500


@app.route("/debug", methods=["GET"])
def debug():
    import datetime
    rows = get_all_rows()
    today = datetime.date.today().strftime("%A")
    return jsonify({"today": today, "rows": rows}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
