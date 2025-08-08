# resume_builder.py
import google.generativeai as genai
import json
import os

try:
    # Reads the GEMINI_API_KEY from the GitHub Actions secret
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY secret not found!")
    
    genai.configure(api_key=gemini_api_key)
    MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')

except Exception as e:
    print(f"[ERROR] Gemini API could not be configured. Details: {e}")
    MODEL = None


def load_master_profile():
    """Loads the master profile from the JSON file."""
    try:
        with open('master_profile.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] master_profile.json not found!")
        return None

def generate_tailored_resume_text(job_description):
    """
    Uses the Gemini AI to generate a tailored resume summary and bullet points.
    """
    if not MODEL:
         return "AI functionality disabled: Gemini API Key not configured or model failed to initialize."

    master_profile = load_master_profile()
    if not master_profile:
        return "Could not generate text: Master profile is missing."

    prompt = f"""
    Based on my master profile below and the following job description, please perform two tasks and provide the output in plain text without any markdown formatting:
    1.  Write a 2-3 sentence professional summary that perfectly aligns my skills with the job's key requirements.
    2.  From my 'work_experience' bullet points, select and rewrite the 3 most relevant points that directly match what the company is looking for in the job description.

    **Job Description:**
    ---
    {job_description}
    ---

    **My Master Profile:**
    ---
    {json.dumps(master_profile, indent=2)}
    ---

    **Output (format exactly as below in plain text):**
    AI Summary:
    [Your generated professional summary here]
    AI-Selected Experience:
    - [Rewritten bullet point 1]
    - [Rewritten bullet point 2]
    - [Rewritten bullet point 3]
    """

    try:
        print("[AI] Generating tailored resume content...")
        response = MODEL.generate_content(prompt)
        print("[AI] Successfully generated content.")
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to generate content from Gemini AI: {e}")
        return "Error generating AI content."
