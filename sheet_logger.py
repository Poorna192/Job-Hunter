import gspread
from google.oauth2.service_account import Credentials
import os
import json

def log_job_to_sheet(title, company, location, link, description, status):
    """
    Logs job details to a Google Sheet using credentials from a GitHub Secret.
    Returns True if successful, False otherwise.
    """
    try:
        gcp_sa_key_json = os.environ.get("GCP_SA_KEY")
        if not gcp_sa_key_json:
            print("[ERROR] Google Cloud service account key not found in GCP_SA_KEY.")
            return False

        credentials_info = json.loads(gcp_sa_key_json)

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)

        client = gspread.authorize(credentials)
        spreadsheet = client.open("Job Tracker")
        sheet = spreadsheet.sheet1

        sheet.append_row([title, company, location, link, description, status])
        print(f"[SUCCESS] Logged job to Google Sheet: {title}")
        return True

    except gspread.exceptions.SpreadsheetNotFound:
        print("[ERROR] Spreadsheet 'Job Tracker' not found. Create it and share it with your service account email.")
    except Exception as e:
        print(f"[ERROR] Failed to log job to Google Sheet: {e}")

    return False
