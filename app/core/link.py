import os
import requests
import json
from urllib.parse import quote

from dotenv import load_dotenv, find_dotenv

from app.core.logger import get_logger

# Load .env reliably even when run from different CWDs
load_dotenv(find_dotenv(), override=True)

logger = get_logger(__name__)


def search_linkedin_jobs(keywords, start=0, count=25, geo_id="105214831", distance=25):
    # join keywords with |
    keywords_str = " | ".join(keywords)

    query_id = "voyagerJobsDashJobCards.909b0d446794dad30bb8a39a7f8997a4"

    # variables = f"(count:{count},query:(selectedFilters:List((key:distance,value:List({distance}))),locationUnion:(geoId:{geo_id}),origin:SEMANTIC_SEARCH_HISTORY,keywords:{keywords_str}),start:{start})"

    variables = "(count:25,query:(selectedFilters:List((key:distance,value:List(25))),locationUnion:(geoId:105214831),origin:SEMANTIC_SEARCH_HISTORY,keywords:Spring%20Boot%20%7C%20java%20%7C%20python%20%7C%20exp),start:25)"
    url = "https://www.linkedin.com/voyager/api/graphql"
    params = {
        "variables": variables,
        "queryId": query_id
    }

    # --- Use full cookie string from Postman/DevTools ---
    cookie_str = os.getenv("LINKEDIN_LI_AT")  # save full Cookie header in .env

    jsessionid = os.getenv("JSESSIONID")
    full_cookies = os.getenv("LINKEDIN_FULL_COOKIES")

    logger.info(f"Cookies: {cookie_str}, {jsessionid}")

    cookies = {
        "li_at" : cookie_str,
        "JSESSIONID" : jsessionid
    }



    if not jsessionid:
        raise ValueError("JSESSIONID not found in cookies")

    headers = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-US,en;q=0.9",
        "csrf-token": jsessionid.strip('"'),
        "referer": f"https://www.linkedin.com/jobs/search-results/?distance={distance}&geoId={geo_id}&keywords={keywords_str}&origin=SEMANTIC_SEARCH_HISTORY",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0",
        "content-type": "application/json",
        "Cookie": f"{full_cookies}"
    }

    logger.info(f"headers: {headers}")
    resp = requests.get(url, headers=headers, cookies=cookies, params=params)

    if resp.status_code != 200:
        raise Exception(f"Failed to fetch jobs: {resp.status_code}, {resp.text}")

    return resp.json()




if __name__ == "__main__":
    # Use raw_variables from your working cURL for 1:1 parity test
    jobs_data = search_linkedin_jobs(["Spring Boot", "java", "python"], start=10, count=25,geo_id="105214831")
    print(json.dumps(jobs_data, indent=2))