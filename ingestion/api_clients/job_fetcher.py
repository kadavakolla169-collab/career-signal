import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
ROLES = ["data engineer", "data scientist", "data analyst"]
API_URL = "https://jsearch.p.rapidapi.com/search"
OUTPUT_FOLDER = "data/raw"
API_KEY = os.environ.get("RAPIDAPI_KEY")
def fetch_jobs(role):
    headers = {
        "x-rapidapi-host" : "jsearch.p.rapidapi.com",
        "x-rapidapi-key" : API_KEY
    }
    params ={
        "query" : f"{role} jobs in USA",
        "page" : "1",
        "num_pages" : "2"
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        return response.json()
    except Exception as e:
        print(f"Error fetching jobs for {role}: {e}")
        return None
    
def save_jobs(data, role):
    filename = role.replace(" ", "_") + "_jobs.json"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} jobs for {role} to {filepath}")

def run():
    for role in ROLES:
        api_response = fetch_jobs(role)
        if api_response is None:
            print(f"Skipping {role} due to API error")
            continue
        data = api_response["data"]
        save_jobs(data, role)
if __name__ == "__main__":
    run()
