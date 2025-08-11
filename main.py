from job_scraper import fetch_all_jobs
from notifier import send_telegram_alert, send_no_jobs_found_alert
from jd_filter import filter_relevant_jobs
from sheet_logger import log_job_to_sheet
from resume_builder import generate_tailored_resume_text
from pdf_generator import create_resume_pdf
from datetime import datetime
import time
import traceback
import json
import os

QUERY = "Cybersecurity OR Ethical Hacking OR Penetration Testing OR Cybersecurity Internship OR Cybersecurity Trainee"
LOCATION = "India"
POSTED_WITHIN_HOURS = 1
CHECK_INTERVAL_SECONDS = 3600
SEEN_JOBS_FILE = 'seen_jobs.json'

def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_seen_jobs(seen_jobs_set):
    with open(SEEN_JOBS_FILE, 'w') as f:
        json.dump(list(seen_jobs_set), f)

def run_job_search(seen_jobs):
    try:
        print(f"\n[INFO] Starting job search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        jobs = fetch_all_jobs(QUERY, LOCATION, POSTED_WITHIN_HOURS)
        print(f"[INFO] Found {len(jobs)} raw jobs.")

        filtered_jobs = filter_relevant_jobs(jobs)
        print(f"[INFO] {len(filtered_jobs)} jobs after filtering.")

        new_jobs_found = 0
        for job in filtered_jobs:
            job_id = f"{job.get('title', '')}-{job.get('company', '')}-{job.get('link', '')}"
            if job_id not in seen_jobs:
                new_jobs_found += 1
                print(f"[INFO] New job found: {job['title']}. Analyzing...")
                
                job_desc_snippet = job.get('description', '')[:1000]
                tailored_content = generate_tailored_resume_text(job_desc_snippet)
                job['ai_resume'] = tailored_content

                pdf_filename = create_resume_pdf(job, tailored_content)
                job['pdf_filename'] = pdf_filename

                send_telegram_alert(job)
                log_job_to_sheet(
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    location=job.get('location', ''),
                    link=job.get('link', ''),
                    description=job.get('description', ''),
                    status="Notified & PDF Generated"
                )
                seen_jobs.add(job_id)
        
        if new_jobs_found > 0:
            save_seen_jobs(seen_jobs)
        else:
            print("[INFO] No new jobs found in this cycle. Sending status alert.")
            send_no_jobs_found_alert()

    except Exception as e:
        print(f"[ERROR] An exception occurred during the job search cycle: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("[INFO] AI Job Agent started in continuous mode.")
    seen_jobs_set = load_seen_jobs()
    print(f"[INFO] Loaded {len(seen_jobs_set)} previously seen jobs.")
    
    while True:
        run_job_search(seen_jobs_set)
        print(f"[INFO] Search cycle complete. Sleeping for {CHECK_INTERVAL_SECONDS / 60} minutes...")
        time.sleep(CHECK_INTERVAL_SECONDS)
