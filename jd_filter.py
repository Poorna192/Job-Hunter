# jd_filter.py - Smart Job Filter
from typing import List, Dict
import re

def filter_relevant_jobs(jobs: List[Dict]) -> List[Dict]:
    # Keywords for entry-level/intern cybersecurity roles
    desired_keywords = [
        "penetration tester", "ethical hacker", "red team", "bug bounty",
        "vulnerability assessor", "application security", "offensive security",
        "cybersecurity", "security consultant", "security researcher",
        "soc analyst", "incident responder", "cyber threat", "intrusion detection",
        "threat hunter", "network security", "security engineer",
        "information security", "digital forensics", "malware analyst",
        "security auditor", "it auditor", "security compliance", "risk analyst",
        "infosec", "security analyst", "cyber defense", "cyber risk",
        "intern"
    ]

    # Set to filter for 0-2 years of experience
    max_exp_required = 2
    relevant_jobs = []

    print("\n[FILTER] Starting job filtering process (0-2 years experience)...")
    for job in jobs:
        title = job.get("title", "").lower()
        desc = job.get("description", "").lower()
        combined_text = title + " " + desc

        # Rule 1: Must contain at least one of the desired keywords
        if not any(keyword in combined_text for keyword in desired_keywords):
            continue

        # Rule 2: Skip roles that are explicitly senior
        senior_match = re.search(r"\b(senior|lead|manager|architect|principal|staff)\b", combined_text)
        if senior_match:
            print(f"[FILTER] Skipping '{title}': Contains senior keyword '{senior_match.group(0)}'.")
            continue
        
        # Rule 3: Skip roles asking for more than max_exp_required years
        exp_matches = re.findall(r'(\d+)\+?\s*-\s*\d+\s+years?|(\d+)\+?\s+years?', combined_text)
        
        found_high_experience = False
        for match in exp_matches:
            for year_str in match:
                if year_str and int(year_str) > max_exp_required:
                    print(f"[FILTER] Skipping '{title}': Requires {year_str} years of experience.")
                    found_high_experience = True
                    break
            if found_high_experience:
                break
        
        if found_high_experience:
            continue
        
        # If all checks pass, it's a relevant job
        print(f"[FILTER] ✅ Keeping '{title}': Looks like a good fit!")
        relevant_jobs.append(job)

    return relevant_jobs
