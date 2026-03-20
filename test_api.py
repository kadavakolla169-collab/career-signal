import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("RAPIDAPI_KEY")
url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
    "x-rapidapi-key": api_key
}
params = {
    "query": "data engineer jobs in USA",
    "page": "1",
    "num_pages": "1"
}
response = requests.get(url, headers=headers, params=params)
#print(response.json()) which just dumps everything in one messy line, json.dumps() does the same thing but formats it nicely with indentation
with open("data/raw/jobs_sample.json", "w") as f:
    json.dump(response.json(), f, indent= 2)
print("Data Saved Successfully")