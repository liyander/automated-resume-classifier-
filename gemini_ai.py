import google.generativeai as genai
import PyPDF2
import io

GEMINI_API_KEY = "AIzaSyDxtJBonwu-tU-U2XcSTlG05eTgGKwyiq0"  
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
def analyze_resume(resume_path, job_title, experience, certifications):
    resume_text = ''
    
    try:
        with open(resume_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                resume_text += page.extract_text() + '\n'
    except:
        encodings = ['utf-8', 'latin-1', 'utf-16']
        for encoding in encodings:
            try:
                with open(resume_path, 'r', encoding=encoding) as file:
                    resume_text = file.read()
                    break
            except (UnicodeDecodeError, IOError):
                continue

    prompt = f"""Comprehensively analyze this resume for a {job_title} position:
    {resume_text}
    
    Analyze ALL qualifications including:
    - Technical skills (both matching and additional ones)
    - All project experience (focusing on security-related tasks)
    - Complete education background (highlight cybersecurity relevance)
    - Total years of professional experience
    - Any certifications (both matching and additional)
    - Other relevant achievements (CTF rankings, bug bounties, etc.)
    
    Provide your response in this EXACT format:
    
    Recommendation Level: [Highly Recommended/Recommended/Moderately Recommended/Not Recommended]
    Recommendation Reason: [detailed justification]
    Additional Qualifications: [list of additional relevant skills]
    Percentage Match: [0-100%]
    Project Experience: [detailed analysis of projects]
    Experience Gap: [key missing qualifications]
    Full Analysis: [comprehensive analysis including all requested points]
    
    Be precise and don't overlook any qualifications. Include specific examples from projects."""
    
    gemini_response = model.generate_content(prompt)

    analysis_results = {
        'suitability': gemini_response.text.split('Recommendation Level:')[1].split('\n')[0].strip(),
        'recommendation_reason': gemini_response.text.split('Recommendation Reason:')[1].split('\n')[0].strip(),
        'additional_qualifications': gemini_response.text.split('Additional Qualifications:')[1].split('\n')[0],
        'entities': [tuple(entity.split(':')) for entity in gemini_response.text.split('Key Entities:')[1].split('\n')[0].strip().split(',')] if 'Key Entities:' in gemini_response.text else [],
        'gemini_analysis': gemini_response.text.split('Full Analysis:')[1].strip() if 'Full Analysis:' in gemini_response.text else gemini_response.text,
        'skill_match_percentage': gemini_response.text.split('Percentage Match:')[1].split('\n')[0].strip(),
        'projects_analysis': gemini_response.text.split('Project Experience:')[1].split('Experience Gap:')[0].strip() if 'Project Experience:' in gemini_response.text else 'Not Available',
        'experience_gap': gemini_response.text.split('Experience Gap:')[1].split('\n')[0].strip()
    }

    return analysis_results
