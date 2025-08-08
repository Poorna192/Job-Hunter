# notifier.py
import requests
import html
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime
import os

def send_telegram_alert(job):
    """Sends a detailed notification for a new job, including the PDF resume."""
    # --- Send the Text Message First ---
    title = html.escape(job.get('title', 'No Title'))
    company = html.escape(job.get('company', 'No Company'))
    location = html.escape(job.get('location', 'No Location'))
    link = job.get('link', '#')

    message = f"""
🚨 <b>New Job Alert!</b>

<b>Title:</b> {title}
<b>Company:</b> {company}
<b>Location:</b> {location}
🔗 <a href="{link}">Apply Here</a>
"""

    if 'ai_resume' in job and job['ai_resume']:
        ai_content = html.escape(job['ai_resume'])
        message += f"""
---
🤖 <b>AI Analysis</b> 🤖
---
<pre>{ai_content}</pre>
"""

    text_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        requests.post(text_url, data=payload, timeout=10)
        print("[+] Text alert sent ✅")
    except Exception as e:
        print(f"[-] An exception occurred while sending text alert: {e}")

    # --- Now, Send the PDF Document ---
    pdf_filename = job.get('pdf_filename')
    if pdf_filename and os.path.exists(pdf_filename):
        doc_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        files = {'document': open(pdf_filename, 'rb')}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        
        try:
            response = requests.post(doc_url, data=data, files=files, timeout=15)
            if response.status_code == 200:
                print(f"[+] PDF resume '{pdf_filename}' sent ✅")
            else:
                print(f"[-] Failed to send PDF ❌. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"[-] An exception occurred while sending PDF: {e}")
    elif pdf_filename:
        print(f"[ERROR] Could not find PDF file to send: {pdf_filename}")


def send_no_jobs_found_alert():
    """Sends a notification when no new relevant jobs are found."""
    current_time = datetime.now().strftime('%I:%M %p')
    message = f"""
✅ <b>Agent Status Update</b> ({current_time})

No new relevant jobs were found in the last search cycle. The agent is still running and will check again in the next hour.
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("[+] 'No jobs found' status alert sent ✅")
        else:
            print(f"[-] Failed to send status alert ❌. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[-] An exception occurred while sending status alert: {e}")
