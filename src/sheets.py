import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Expected sheet format:
# Column A: Day (Monday, Tuesday, etc.)
# Column B: Breakfast
# Column C: Lunch
# Column D: Dinner
# Column E: Snacks (optional)

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"],
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_todays_meals() -> dict | None:
    """
    Reads today's meal plan from Google Sheets by day of week.
    Returns a dict like:
    {
        "date": "Monday",
        "breakfast": "Poha, Chai",
        "lunch": "Dal, Rice, Sabzi, Roti",
        "dinner": "Khichdi, Papad",
        "snacks": "Samosa"   # optional
    }
    Returns None if today's entry is not found.
    """
    service = get_service()
    # print(service, 'service')
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    range_name = os.environ.get("SHEET_RANGE", "A:E")

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name)
        .execute()
    )
    # print(result, 'result')

    rows = result.get("values", [])
    if not rows:
        print("No data found in sheet.")
        return None

    today = datetime.date.today().strftime("%A")  # e.g. "Monday"
    print(today, 'today')

    for row in rows[1:]:  # skip header row
        if not row:
            continue
        date_cell = row[0].strip() if len(row) > 0 else ""
        print(date_cell, 'date_cell')
        if date_cell.lower() == today.lower():
            return {
                "date": today,
                "breakfast": row[1].strip() if len(row) > 1 else "—",
                "lunch":     row[2].strip() if len(row) > 2 else "—",
                "dinner":    row[3].strip() if len(row) > 3 else "—",
                "snacks":    row[4].strip() if len(row) > 4 else None,
            }

    print(f"No entry found for today ({today}). Check sheet has a row with that day name.")
    return None


def get_all_rows() -> list:
    service = get_service()
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    range_name = os.environ.get("SHEET_RANGE", "A:E")
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])
