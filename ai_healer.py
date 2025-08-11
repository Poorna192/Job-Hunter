import google.generativeai as genai
import os
import json

try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY secret not found!")
    
    genai.configure(api_key=gemini_api_key)
    MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')

except Exception as e:
    print(f"[ERROR] AI Healer could not be initialized. Details: {e}")
    MODEL = None

def get_new_selector(html_content, element_description, old_selector):
    if not MODEL:
        return None

    body_start = html_content.lower().find('<body')
    if body_start != -1:
        html_content = html_content[body_start:]
    
    html_snippet = html_content[:25000]

    prompt = f"""
    I am a Python web scraper using BeautifulSoup. My goal is to find the '{element_description}'.
    I was using the CSS selector '{old_selector}', but it has stopped working.
    
    Based on the following HTML snippet, please provide the new, correct CSS selector to find the '{element_description}'.
    Your response should contain ONLY the CSS selector and nothing else.

    HTML Snippet:
    ---
    {html_snippet}
    ---

    New CSS Selector:
    """

    try:
        print(f"[AI HEALER] Asking AI for a new selector for '{element_description}'...")
        response = MODEL.generate_content(prompt)
        new_selector = response.text.strip()
        
        if " " in new_selector or "." in new_selector or "#" in new_selector:
            print(f"[AI HEALER] AI suggested new selector: '{new_selector}'")
            return new_selector
        else:
            print(f"[AI HEALER] AI returned an invalid or empty selector: '{new_selector}'")
            return None

    except Exception as e:
        print(f"[ERROR] AI Healer failed to get a new selector: {e}")
        return None

def update_selectors_file(site, element, new_selector):
    with open('scraper_selectors.json', 'r+') as f:
        selectors = json.load(f)
        selectors[site][element] = new_selector
        f.seek(0)
        json.dump(selectors, f, indent=2)
        f.truncate()
    print(f"[AI HEALER] Successfully updated 'scraper_selectors.json' for {site}.{element}")
