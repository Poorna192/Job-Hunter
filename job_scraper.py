import os
import time
import random
import logging
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

try:
    from jd_filter import filter_relevant_jobs
except Exception:
    filter_relevant_jobs = None

try:
    from sheet_logger import log_job_to_sheet
except Exception:
    log_job_to_sheet = None

try:
    from notifier import send_telegram_alert
except Exception:
    send_telegram_alert = None

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_BASE = "https://serpapi.com/search.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36"
}


def _random_sleep(min_s=0.6, max_s=1.8):
    time.sleep(random.uniform(min_s, max_s))


def fetch_google_jobs(query, location="India", limit=10):
    if not SERPAPI_KEY:
        LOG.warning("SERPAPI_KEY not set. Skipping Google Jobs.")
        return []

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "api_key": SERPAPI_KEY,
        "hl": "en"
    }
    try:
        resp = requests.get(SERPAPI_BASE, params=params, headers=DEFAULT_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        LOG.error("Google Jobs (SerpApi) request failed: %s", e)
        return []

    jobs = []
    for job in data.get("jobs_results", [])[:limit]:
        title = job.get("title")
        company = job.get("company_name")
        location_txt = job.get("location")
        description = job.get("description") or ""
        link = ""
        for opt in job.get("apply_options", []):
            if opt.get("link"):
                link = opt.get("link")
                break
        if not link:
            for opt in job.get("related_links", []):
                if opt.get("link"):
                    link = opt.get("link")
                    break

        jobs.append({
            "title": title or "",
            "company": company or "",
            "location": location_txt or "",
            "description": description.strip(),
            "link": link or "",
            "source": "Google Jobs"
        })
    LOG.info("Google Jobs: fetched %d jobs for query=%s", len(jobs), query)
    return jobs


def fetch_ambitionbox_jobs(query, location="India", pages=1):
    base = "https://www.ambitionbox.com/jobs/search"
    jobs = []
    for page in range(1, pages + 1):
        url = f"{base}?title={quote_plus(query)}&location={quote_plus(location)}&page={page}"
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            LOG.error("AmbitionBox request failed: %s", e)
            break

        candidate_selectors = [
            "div.jobCard",
            "div.ab_serp_result",
            "article.jobCard"
        ]
        job_cards = []
        for sel in candidate_selectors:
            job_cards = soup.select(sel)
            if job_cards:
                break

        if not job_cards:
            job_cards = soup.select("a.result-title")

        for card in job_cards:
            title_tag = card.select_one("h2 > a") or card.select_one("a.job-title") or card.select_one("a.result-title")
            title = title_tag.get_text(strip=True) if title_tag else None

            comp_tag = card.select_one(".company") or card.select_one(".companyName") or card.select_one(".company-info a")
            company = comp_tag.get_text(strip=True) if comp_tag else None

            loc_tag = card.select_one(".location") or card.select_one(".locWdgt") or card.select_one(".jobCard__location")
            location_txt = loc_tag.get_text(strip=True) if loc_tag else location

            link = ""
            if title_tag and title_tag.has_attr("href"):
                link = title_tag["href"]
                if link.startswith("/"):
                    link = "https://www.ambitionbox.com" + link

            desc_tag = card.select_one(".job-snippet") or card.select_one(".short-desc") or card.select_one(".info")
            description = desc_tag.get_text(" ", strip=True) if desc_tag else ""

            if title and company:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_txt,
                    "description": description,
                    "link": link,
                    "source": "AmbitionBox"
                })

        _random_sleep(0.5, 1.2)

    LOG.info("AmbitionBox: fetched %d jobs for query=%s", len(jobs), query)
    return jobs


def fetch_glassdoor_jobs(query, location="India", pages=1):
    jobs = []
    for page in range(1, pages + 1):
        safe_query = quote_plus(query)
        safe_location = quote_plus(location)
        url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={safe_query}&locT=C&locId=&locKeyword={safe_location}&p={page}"

        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            LOG.error("Glassdoor request failed: %s", e)
            break

        candidate_selectors = [
            "li.react-job-listing",
            "li.jl",
            "div.jobContainer"
        ]
        job_cards = []
        for sel in candidate_selectors:
            job_cards = soup.select(sel)
            if job_cards:
                break

        if not job_cards:
            job_cards = soup.select("div.EiJobCard") or []

        for card in job_cards:
            title_tag = card.select_one("a.jobLink") or card.select_one("a.eiJobLink") or card.select_one(".jobTitle")
            title = (title_tag.get_text(strip=True) if title_tag else None)

            company_tag = card.select_one(".jobEmpolyerName") or card.select_one(".jobEmpolyerName a") or card.select_one(".jobHeader a")
            company = (company_tag.get_text(strip=True) if company_tag else None)

            loc_tag = card.select_one(".loc") or card.select_one(".subtle.loc") or card.select_one(".jobLocation")
            location_txt = (loc_tag.get_text(strip=True) if loc_tag else location)

            link = ""
            if title_tag and title_tag.has_attr("href"):
                link = title_tag["href"]
                if link.startswith("/"):
                    link = "https://www.glassdoor.co.in" + link

            desc_tag = card.select_one(".jobSnippet") or card.select_one(".job-snippet") or card.select_one(".jobDesc")
            description = desc_tag.get_text(" ", strip=True) if desc_tag else ""

            if title and company:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_txt,
                    "description": description,
                    "link": link,
                    "source": "Glassdoor"
                })

        _random_sleep(0.6, 1.6)

    LOG.info("Glassdoor: fetched %d jobs for query=%s", len(jobs), query)
    return jobs


def dedupe_jobs(jobs):
    seen = set()
    unique = []
    for j in jobs:
        key = (j.get("title", "").lower(), j.get("company", "").lower(), (j.get("link") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(j)
    return unique


def fetch_all_jobs(query="cybersecurity", location="India", pages=1):
    all_jobs = []
    queries = [query, "ethical hacking", "penetration tester"]
    for q in queries:
        all_jobs.extend(fetch_google_jobs(q, location, limit=10))
        all_jobs.extend(fetch_ambitionbox_jobs(q, location, pages=pages))
        all_jobs.extend(fetch_glassdoor_jobs(q, location, pages=pages))

    all_jobs = dedupe_jobs(all_jobs)

    if filter_relevant_jobs:
        try:
            all_jobs = filter_relevant_jobs(all_jobs)
        except Exception as e:
            LOG.error("filter_relevant_jobs failed: %s", e)

    for job in all_jobs:
        try:
            if log_job_to_sheet:
                try:
                    log_job_to_sheet(
                        title=job.get("title", ""),
                        company=job.get("company", ""),
                        location=job.get("location", ""),
                        link=job.get("link", ""),
                        description=job.get("description", ""),
                        status="scraped"
                    )
                except TypeError:
                    log_job_to_sheet(job)
        except Exception as e:
            LOG.debug("Logging to sheet failed: %s", e)

        try:
            if send_telegram_alert:
                send_telegram_alert(job)
        except Exception as e:
            LOG.debug("Telegram alert failed: %s", e)

    LOG.info("Total jobs returned: %d", len(all_jobs))
    return all_jobs


if __name__ == "__main__":
    results = fetch_all_jobs("cybersecurity", "India", pages=1)
    for r in results:
        print(f"{r['title']} | {r['company']} | {r['location']} | {r['source']}\n{r['link']}\n")
