import os
import json
import psycopg2
import time
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
def extract_skills(job_highlights):
    prompt = EXTRACTION_PROMPT.format(job_description=job_highlights)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    
    response_text = chat_completion.choices[0].message.content
    
    try:
        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse response: {response_text}")
        return None

def get_jobs_from_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("""SELECT job_id, job_highlights, role FROM jobs
                   WHERE job_id NOT IN (SELECT job_id FROM job_skills)
                   AND job_highlights IS NOT NULL
                   AND job_highlights != '{}'
                   """)
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return jobs

def save_skills_to_db(job_id, skills):
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_skills (
            job_id, technical_skills, cloud_platforms,
            experience_level, experience_years,
            visa_sponsorship, education, extracted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE
        ) ON CONFLICT (job_id) DO NOTHING;
    """, (
        job_id,
        json.dumps(skills.get("technical_skills")),
        json.dumps(skills.get("cloud_platforms")),
        skills.get("experience_level"),
        skills.get("experience_years"),
        skills.get("visa_sponsorship"),
        skills.get("education")
    ))
    conn.commit()
    cursor.close()
    conn.close()
    
if __name__ == "__main__":
    jobs = get_jobs_from_db()
    print(f"Found {len(jobs)} jobs to process")
    
    for job_id, job_highlights, role in jobs:
        if not job_highlights or job_highlights == '{}':
            print(f"Skipping {job_id} - no highlights")
            continue
        
        print(f"Processing {role} job: {job_id[:20]}...")
        try:
            skills = extract_skills(job_highlights)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit hit! Stopping gracefully. Run again tomorrow.")
                break
            else:
                print(f"Unexpected error: {e}")
                continue

        if skills:
            save_skills_to_db(job_id, skills)
            print(f"Saved skills for {job_id[:20]}")
            time.sleep(2)
        else:
            print(f"Failed to extract skills for {job_id[:20]}")
    
    print("Done!")