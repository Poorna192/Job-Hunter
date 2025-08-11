import requests
import html
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime
import os

def send_telegram_alert(job):
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
