import gspread
from google.oauth2.service_account import Credentials
import os
import json

def log_job_to_sheet(title, company, location, link, description, status):
    """
    Logs the details of a job to a Google Sheet using credentials from a GitHub Secret.
    """
    try:
        # --- Securely load credentials from environment variable ---
        gcp_sa_key_json = os.environ.get("GCP_SA_KEY")
        if not gcp_sa_key_json:
            print("[ERROR] Google Cloud service account key not found in GitHub Secrets (GCP_SA_KEY).")
            return

        # Convert the JSON string from the environment variable into a dictionary
        credentials_info = json.loads(gcp_sa_key_json)
        # --- End of secure loading ---

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # Authenticate using the credentials dictionary
        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=scopes
        )

        client = gspread.authorize(credentials)

        spreadsheet = client.open("Job Tracker")
        sheet = spreadsheet.sheet1

        row_to_add = [title, company, location, link, description, status]
        sheet.append_row(row_to_add)
        print(f"[INFO] Successfully logged job to Google Sheet: {title}")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"[ERROR] Spreadsheet 'Job Tracker' not found. Please create it and share it with your service account email.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while logging to Google Sheet: {e}")
