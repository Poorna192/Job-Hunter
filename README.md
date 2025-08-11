🤖 AI Job Hunter Pro
An intelligent, autonomous agent that scrapes job boards, filters for relevant roles, and tailors your resume for each application using the Gemini AI.

This isn't just a scraper; it's a complete, automated job application assistant designed to streamline the job hunting process for cybersecurity professionals. The agent works tirelessly, 24/7, to find the best opportunities and prepare a unique, tailored application for each one, ensuring you always put your best foot forward.

✨ Key Features
Multi-Source Scraping: Scans multiple job platforms (LinkedIn, Google Jobs) to aggregate a wide range of opportunities.

Intelligent Filtering: Uses a sophisticated keyword and experience-level filter to discard irrelevant jobs and only focus on entry-level cybersecurity roles.

AI-Powered Resume Tailoring: Leverages the Google Gemini API to analyze each job description and rewrite your professional summary and key experience points to perfectly match the role's requirements.

Automated PDF Generation: Creates a unique, tailored PDF resume for every single job it finds, ready to be submitted.

Instant Notifications: Sends real-time alerts directly to your Telegram with the job details, AI analysis, and the tailored PDF resume attached.

Self-Healing Scrapers (Experimental): An AI-powered module that attempts to automatically fix the web scrapers if a website's layout changes.

Cloud-Ready: Designed to be deployed on a cloud server (like AWS EC2) for continuous, 24/7 operation.

⚙️ How It Works
The project follows a modular, pipeline-based architecture:

Scrape: The job_scraper.py module uses Selenium and the SerpApi to fetch raw job listings from LinkedIn and Google Jobs.

Filter: The raw list is passed to jd_filter.py, which removes senior-level positions and roles that don't match the core cybersecurity keywords.

Analyze & Tailor: For each relevant job, resume_builder.py sends the job description and your master profile to the Gemini AI to generate tailored content.

Generate: pdf_generator.py takes the AI-generated content and creates a new, polished PDF resume.

Notify & Log: notifier.py sends an alert to Telegram, and sheet_logger.py logs the job in a Google Sheet for tracking.

Repeat: The main.py script orchestrates this entire process in a continuous loop.

🛠️ Tech Stack
Core: Python

Web Scraping: Selenium, BeautifulSoup, SerpApi

AI & Machine Learning: Google Gemini API

PDF Generation: FPDF2

Notifications: Telegram API

Data Logging: Google Sheets API, gspread

🚀 Setup and Installation
Follow these steps to get your own AI Job Hunter running.

1. Prerequisites
Python 3.10+

A cloud server (like a free-tier AWS EC2 instance) is recommended for 24/7 operation.

API keys for:

Google Gemini

Telegram Bot

SerpApi

A Google Cloud Service Account JSON key for Google Sheets

2. Clone the Repository
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

3. Set Up a Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.

# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

4. Install Dependencies
Install all the required libraries from the requirements.txt file.

pip install -r requirements.txt

5. Configure Environment Variables
This project uses environment variables to keep your API keys secure. Create a .env file in the root directory and add your keys.

# .env file
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID_HERE"
SERPAPI_KEY="YOUR_SERPAPI_KEY_HERE"
GCP_SA_KEY='{"type": "service_account", "project_id": "...", ...}'

Note: When deploying on a server, it's best to set these as actual environment variables (e.g., in your .bashrc file).

6. Customize Your Profile
Open the master_profile.json file and replace the placeholder content with your own professional details. This is crucial, as the AI uses this information to write your tailored resumes.

▶️ Usage
Once everything is configured, simply run the main script:

python3 main.py

The bot will start its first job search cycle. Sit back and wait for the opportunities to arrive in your Telegram!

