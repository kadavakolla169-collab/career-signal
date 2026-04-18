import psycopg2
import json
import os
from dotenv import load_dotenv
load_dotenv()

ROLES = ["data engineer", "data scientist", "data analyst"]
RAW_DATA_FOLDER = "data/raw"
def get_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    return conn
def load_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    for role in ROLES:
        filename = role.replace(" ", "_") + "_jobs.json"
        filepath = os.path.join(RAW_DATA_FOLDER, filename)

        with open(filepath, "r") as f:
            data = json.load(f)
            for job in data:
                cursor.execute("""
                INSERT INTO jobs (
                    job_id, job_title, employer_name, employer_website,
                    job_apply_link, job_description, job_city, job_state,
                    job_country, job_is_remote, job_min_salary, job_max_salary,
                    job_posted_at, role, job_highlights, date_fetched
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE
                ) ON CONFLICT (job_id) DO UPDATE SET
                job_highlights = EXCLUDED.job_highlights;
            """, (
                job.get("job_id"),
                job.get("job_title"),
                job.get("employer_name"),
                job.get("employer_website"),
                job.get("job_apply_link"),
                job.get("job_description"),
                job.get("job_city"),
                job.get("job_state"),
                job.get("job_country"),
                job.get("job_is_remote"),
                job.get("job_min_salary"),
                job.get("job_max_salary"),
                job.get("job_posted_at"),
                role,
                json.dumps(job.get("job_highlights"))
            ))
    conn.commit()
    cursor.close()
    conn.close()
    print("All jobs loaded successfully!")

if __name__ == "__main__":
    load_jobs()