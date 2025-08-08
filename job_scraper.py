# job_scraper.py
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

# --- Self-Healing Imports ---
from ai_healer import get_new_selector, update_selectors_file

# --- Selenium Imports for LinkedIn ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def load_selectors(site):
    """Loads CSS selectors from the JSON file for a specific site."""
    if not os.path.exists('scraper_selectors.json'):
        raise FileNotFoundError("scraper_selectors.json not found! Please create it.")
    with open('scraper_selectors.json', 'r') as f:
        return json.load(f)[site]

# ---------------- NAUKRI (SELF-HEALING SCRAPER) ----------------
def fetch_jobs_from_naukri_scraper(query, location, posted_within_hours=1):
    selectors = load_selectors('naukri')
    jobs = []
    query_formatted = query.lower().replace(" or ", " ").replace(" ", "-")
    location_formatted = location.lower()
    url = f"https://www.naukri.com/{query_formatted}-jobs-in-{location_formatted}?sort=f"
    print(f"[INFO] Scraping Naukri URL: {url}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        job_elements = soup.select(selectors['job_card'])
        
        # --- Self-Healing Logic ---
        if not job_elements:
            print(f"[HEALER] Could not find job cards on Naukri using selector: '{selectors['job_card']}'. Attempting to self-heal.")
            new_selector = get_new_selector(response.text, "the main container for a single job posting", selectors['job_card'])
            if new_selector:
                update_selectors_file('naukri', 'job_card', new_selector)
                selectors['job_card'] = new_selector
                job_elements = soup.select(selectors['job_card']) # Retry with the new selector
        # --- End Self-Healing ---

        for job_elem in job_elements:
            posted_date_elem = job_elem.select_one(selectors['posted_date'])
            posted_text = posted_date_elem.text.lower() if posted_date_elem else 'unknown'

            if 'hour' in posted_text or 'min' in posted_text or 'just now' in posted_text:
                title_elem = job_elem.select_one(selectors['title'])
                company_elem = job_elem.select_one(selectors['company'])
                loc_elem = job_elem.select_one(selectors['location'])
                
                if title_elem and company_elem and loc_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": loc_elem.text.strip(),
                        "description": job_elem.select_one(selectors['description']).text.strip() if job_elem.select_one(selectors['description']) else "N/A",
                        "link": title_elem['href']
                    })
    except Exception as e:
        print(f"[ERROR] Could not scrape Naukri: {e}")
    
    return jobs

# ---------------- LINKEDIN (SELF-HEALING SCRAPER) ----------------
def fetch_jobs_from_linkedin_scraper(query, location, posted_within_hours=1):
    selectors = load_selectors('linkedin')
    jobs = []
    time_filter = "r86400" if posted_within_hours <= 24 else ""
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&{time_filter}&sortBy=R"
    print(f"[INFO] Scraping LinkedIn URL: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(3)
        page_source = driver.page_source

        job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_card'])

        # --- Self-Healing Logic ---
        if not job_cards:
            print(f"[HEALER] Could not find job cards on LinkedIn using selector: '{selectors['job_card']}'. Attempting to self-heal.")
            new_selector = get_new_selector(page_source, "the main container for a single job posting", selectors['job_card'])
            if new_selector:
                update_selectors_file('linkedin', 'job_card', new_selector)
                selectors['job_card'] = new_selector
                job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_card']) # Retry
        # --- End Self-Healing ---

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, selectors['title']).text.strip()
                company = card.find_element(By.CSS_SELECTOR, selectors['company']).text.strip()
                card_location = card.find_element(By.CSS_SELECTOR, selectors['location']).text.strip()
                link = card.find_element(By.CSS_SELECTOR, selectors['link']).get_attribute('href')
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": card_location,
                    "description": "Description not available via basic scrape.",
                    "link": link
                })
            except Exception:
                continue
    except Exception as e:
        print(f"[ERROR] Could not scrape LinkedIn: {e}")
    finally:
        if driver:
            driver.quit()
    
    return jobs

# ---------------- MASTER FETCHER ----------------
def fetch_all_jobs(query, location, posted_within_hours=1):
    print("[INFO] Relying on custom self-healing scrapers for this run.")
    naukri_jobs = fetch_jobs_from_naukri_scraper(query, location, posted_within_hours)
    linkedin_jobs = fetch_jobs_from_linkedin_scraper(query, location, posted_within_hours)

    all_jobs = naukri_jobs + linkedin_jobs
    print(f"[INFO] Found a total of {len(all_jobs)} jobs from custom scrapers.")
    return all_jobs
