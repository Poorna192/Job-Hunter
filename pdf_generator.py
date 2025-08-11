from fpdf import FPDF
import json
import re

def parse_ai_content(tailored_content):
    summary_match = re.search(r"AI Summary:\s*(.*?)\s*AI-Selected Experience:", tailored_content, re.DOTALL)
    experience_match = re.search(r"AI-Selected Experience:\s*(.*)", tailored_content, re.DOTALL)

    summary = summary_match.group(1).strip() if summary_match else "AI summary could not be parsed."
    
    experience_text = experience_match.group(1).strip() if experience_match else ""
    experience_points = [line.strip().lstrip('- ') for line in experience_text.split('\n') if line.strip()]
    
    return {"summary": summary, "experience": experience_points}

def create_resume_pdf(job, tailored_content):
    try:
        with open('master_profile.json', 'r') as f:
            profile = json.load(f)
    except FileNotFoundError:
        print("[ERROR] Cannot generate PDF: master_profile.json not found.")
        return None

    ai_parts = parse_ai_content(tailored_content)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, profile['personal_info']['name'], 0, 1, 'C')
    pdf.set_font('Helvetica', '', 10)
    contact_info = f"{profile['personal_info']['phone']} | {profile['personal_info']['email']} | {profile['personal_info']['linkedin']}"
    pdf.cell(0, 10, contact_info, 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Professional Summary', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, ai_parts['summary'])
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Relevant Experience', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    for point in ai_parts['experience']:
        pdf.multi_cell(0, 5, f'• {point}')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Technical Skills', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    skills_text = ", ".join(profile['skills']['technical_concepts'] + profile['skills']['programming'] + profile['skills']['tools_and_platforms'])
    pdf.multi_cell(0, 5, skills_text)
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Projects', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    for project in profile['projects']:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 5, project['name'], 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, project['description'])
        pdf.ln(2)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Education', 0, 1)
    pdf.set_font('Helvetica', 'B', 10)
    education = profile['education'][0]
    pdf.cell(0, 5, f"{education['degree']} - {education['institution']}", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f"Graduated: {education['dates']} | GPA: {education['gpa']}", 0, 1)
    
    company_name = job.get('company', 'UnknownCompany').replace(' ', '_')
    filename = f"Resume_Poornachandra_for_{company_name}.pdf"
    pdf.output(filename)
    print(f"[SUCCESS] Generated PDF resume: {filename}")
    return filename
