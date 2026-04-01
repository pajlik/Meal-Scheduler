import os
import requests


def build_message(meals: dict) -> str:
    """
    Formats the meal dict into a clean WhatsApp message.
    """
    date = meals["date"]
    lines = [
        f"🍽️ *कल का मेनू ({date})!*\n",
        f"🌅 *नाश्ता (Breakfast):*\n{meals['breakfast']}\n",
        f"☀️ *दोपहर का खाना (Lunch):*\n{meals['lunch']}\n",
        f"🌙 *रात का खाना (Dinner):*\n{meals['dinner']}",
    ]
    if meals.get("snacks"):
        lines.append(f"\n☕ *स्नैक्स (Snacks):*\n{meals['snacks']}")

    lines.append("\nधन्यवाद! 🙏")
    return "\n".join(lines)


def send_whatsapp_message(meals: dict) -> bool:
    """
    Sends a WhatsApp message to the cook via Green API.
    Returns True if successful, False otherwise.
    """
    instance_id    = os.environ["GREEN_API_INSTANCE_ID"]
    instance_token = os.environ["GREEN_API_TOKEN"]
    to_number      = os.environ["COOK_WHATSAPP_NUMBER"]  # format: 91XXXXXXXXXX

    message_body = build_message(meals)

    base_url = os.environ.get("GREEN_API_BASE_URL", "https://api.green-api.com")
    url = f"{base_url}/waInstance{instance_id}/sendMessage/{instance_token}"

    chat_id = to_number if "@" in to_number else f"{to_number}@c.us"
    payload = {
        "chatId": chat_id,
        "message": message_body,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"✅ Message sent successfully to {to_number}")
        return True
    else:
        print(f"❌ Failed to send message: {response.status_code} — {response.text}")
        return False
