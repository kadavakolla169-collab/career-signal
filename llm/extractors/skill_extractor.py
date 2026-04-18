import os
import json
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
EXTRACTION_PROMPT = """
You are a job description analyzer.
Extract the following from this job description and return ONLY a JSON object with no explanation:
- technical_skills: list of technical skills required
- cloud_platforms: list of cloud platforms mentioned
- experience_level: one of "entry", "mid", "senior"
- experience_years: minimum years of experience as a number or null
- visa_sponsorship: true, false, or null if not mentioned
- education: minimum education required or null

Job description:
{job_description}

Return ONLY valid JSON. No explanation, no markdown, no code blocks.
"""
def extract_skills(job_description):
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    
    response_text = chat_completion.choices[0].message.content
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse response: {response_text}")
        return None

if __name__ == "__main__":
    test_description = "We are looking for a Data Engineer with 3+ years of experience in Python, SQL, and AWS. Experience with dbt and Airflow required. Bachelor's degree in Computer Science. We do not offer visa sponsorship."
    
    result = extract_skills(test_description)
    print(json.dumps(result, indent=2))