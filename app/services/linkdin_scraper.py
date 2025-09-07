import os
import requests
import json
from urllib.parse import quote

from dotenv import load_dotenv

from app.core.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


def get_linkedin_jobs(keywords: list, count: int = 25, start: int = 0):
    """
    Fetches job listings from LinkedIn's internal API based on a list of keywords.

    This function requires two environment variables to be set for authentication:
    - LINKEDIN_COOKIE: The full cookie string from your browser session.
    - CSRF_TOKEN: The 'csrf-token' value, which is often the same as the JSESSIONID value.

    Args:
        keywords: A list of strings representing the job keywords to search for.
        count: The number of job listings to retrieve (default is 25).
        start: The starting index for pagination (default is 0).

    Returns:
        A dictionary containing the API response (job data) or an error message.
    """
    # 1. Load authentication details from environment variables
    cookie = os.getenv("LINKEDIN_COOKIE")
    csrf_token = os.getenv("CSRF_TOKEN")

    if not cookie or not csrf_token:
        return {
            "error": "Environment variables not set.",
            "message": "Please set 'LINKEDIN_COOKIE' and 'CSRF_TOKEN' environment variables."
        }

    # 2. Format and URL-encode the keywords string.
    # This is the only part of the 'variables' parameter that needs encoding.
    # quote() uses %20 for spaces, which matches the original request.
    keywords_string = " | ".join(keywords)
    encoded_keywords = quote(keywords_string)

    # 3. Construct the 'variables' parameter value using the function arguments.
    # We insert the pre-encoded keywords string here. The parentheses and colons
    # will be passed as literal characters because we will build the URL manually.
    # The order of keys inside 'query' has also been matched to the working curl command.
    variables_param_value = (
        f"(count:{count},query:(selectedFilters:List((key:distance,value:List(25))),"
        f"locationUnion:(geoId:105214831),origin:SEMANTIC_SEARCH_HISTORY,"
        f"keywords:{encoded_keywords}),start:{start})"
    )

    # 4. Define the other parameters and the base URL
    base_url = "https://www.linkedin.com/voyager/api/graphql"
    query_id_param_value = "voyagerJobsDashJobCards.909b0d446794dad30bb8a39a7f8997a4"

    # 5. Manually construct the full URL.
    # This prevents the `requests` library from automatically (and incorrectly)
    # encoding the special characters in the 'variables' parameter.
    url = f"{base_url}?variables={variables_param_value}&queryId={query_id_param_value}"

    # 6. Set up the necessary headers, mimicking the browser
    headers = {
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': cookie,
        'csrf-token': csrf_token,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-restli-protocol-version': '2.0.0',
        'referer': 'https://www.linkedin.com/jobs/search/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }

    # 7. Make the GET request and handle the response
    try:
        # We pass the fully constructed URL and no 'params' dictionary
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {"error": "HTTP Error", "message": str(http_err), "status_code": response.status_code,
                "response_text": response.text}
    except requests.exceptions.RequestException as req_err:
        return {"error": "Request Exception", "message": str(req_err)}
    except json.JSONDecodeError:
        return {"error": "JSON Decode Error", "message": "Failed to parse response from LinkedIn.",
                "response_text": response.text}


def parse_job_data(response_data: dict):
    """
    Parses the raw API response to extract a clean list of job postings.

    Args:
        response_data: The JSON dictionary returned by the get_linkedin_jobs function.

    Returns:
        A list of dictionaries, where each dictionary represents a job
        with its title and posting ID. Returns an empty list if data is not found.
    """
    jobs_list = []
    if "error" in response_data:
        print(f"Cannot parse data due to API error: {response_data.get('message')}")
        return jobs_list

    try:
        # Navigate through the nested JSON to find the list of job elements
        elements = response_data['data']['data']['jobsDashJobCardsBySemanticSearch']['elements']
        for element in elements:
            # The actual job card data is nested within the element
            try:
                job_url = element['jobCard']['jobPostingCardWrapper']['jobTrackingData']['navigationAction']['actionTarget']
                jobs_list.append(job_url)
            except (KeyError, TypeError):
                continue



    except (KeyError, TypeError) as e:
        print(f"Error parsing response JSON. The structure might have changed. Details: {e}")

    return jobs_list

def parse_job_id_from_urls(urls : list):
    # "https://www.linkedin.com/jobs/search-results/?currentJobId=4281804988&keywords=Spring%20Boot%20%7C%20java%20%7C%20python%20%7C%20devops&distance=25&geoId=105214831&origin=SEMANTIC_SEARCH_HISTORY&trackingId=8ZUuMsqLI7WRSkQtNd40MA%3D%3D&refId=BkRMRg0YwT7O7q1w8YzLMA%3D%3D&eBP=NON_CHARGEABLE_CHANNEL",
    job_ids = []
    for url in urls:
        logger.info(f"Parsing job ID from URL: {url}")
        job_ids.append(url.split("currentJobId=")[1].split("&")[0])
    return job_ids

def get_linkedin_job_details(job_id: str):
    """
    Fetches job details from the LinkedIn API based on a job ID.

    This function requires environment variables for authentication:
    - LINKEDIN_COOKIE: The full cookie string from your browser session.
    - CSRF_TOKEN: The 'csrf-token' value.

    Args:
        job_id: A string representing the unique ID of the job posting.

    Returns:
        A dictionary containing the API response (job data) or an error message.
    """
    # 1. Load authentication details from environment variables
    cookie = os.getenv("LINKEDIN_COOKIE")
    csrf_token = os.getenv("CSRF_TOKEN")

    if not cookie or not csrf_token:
        return {
            "error": "Environment variables not set.",
            "message": "Please set 'LINKEDIN_COOKIE' and 'CSRF_TOKEN' environment variables."
        }

    # 2. Define the API endpoint URL and query parameters
    base_url = "https://www.linkedin.com/voyager/api/jobs/jobPostings/"
    url = f"{base_url}{job_id}"
    params = {
        'decorationId': 'com.linkedin.voyager.deco.jobs.web.shared.WebLightJobPosting-23',
    }

    # 3. Set up the necessary headers to mimic a browser request
    headers = {
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
        'cookie': cookie,
        'csrf-token': csrf_token,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-li-lang': 'en_US',
        'x-restli-protocol-version': '2.0.0'
    }

    # 4. Make the GET request and handle the response
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {"error": "HTTP Error", "message": str(http_err), "status_code": response.status_code,
                "response_text": response.text}
    except requests.exceptions.RequestException as req_err:
        return {"error": "Request Exception", "message": str(req_err)}
    except json.JSONDecodeError:
        return {"error": "JSON Decode Error", "message": "Failed to parse response from LinkedIn.",
                "response_text": response.text}


def parse_job_json_response(json_response: dict):
    """
    Parses a JSON response from the LinkedIn job details API to extract specific fields.

    Args:
        json_response: A dictionary containing the JSON response from the API.

    Returns:
        A dictionary with the requested job details or None if data is not found.
    """
    if not isinstance(json_response, dict) or "data" not in json_response:
        return {"error": "Invalid JSON response format."}

    job_data = json_response['data']

    # Use .get() with a default value to avoid KeyError
    details = {
        "title": job_data.get('title'),
        "formattedJobLocation": job_data.get('formattedLocation'),
        "workRemoteAllowed": job_data.get('workRemoteAllowed'),
        "listedAt": job_data.get('listedAt'),
        "applyUrl": None,
        "companyprofile": None,
        "company-name": None,
        "companyUniversalName": None,
        "localizedName": None,
        "jobInfo": None,
    }

    # Extract 'localizedName' from the 'included' list by matching the workplaceType urn
    workplace_types = job_data.get('workplaceTypes', [])
    if workplace_types and 'included' in json_response:
        workplace_type_urn = workplace_types[0]
        for item in json_response['included']:
            if item.get('entityUrn') == workplace_type_urn:
                details["localizedName"] = item.get('localizedName')
                break

    # Handle nested data for company details
    company_details = job_data.get('companyDetails', {})
    if company_details:
        company_urn = company_details.get('company')
        for item in json_response.get('included', []):
            if item.get('entityUrn') == company_urn:
                details["companyprofile"] = item.get('url')
                details["company-name"] = item.get('name')
                details["companyUniversalName"] = item.get('universalName')
                break

    # Extract easyApplyUrl or companyApplyUrl
    apply_method = job_data.get('applyMethod', {})
    if apply_method:
        details["applyUrl"] = apply_method.get('easyApplyUrl') or apply_method.get('companyApplyUrl')

    # Extract and clean job description
    description_obj = job_data.get('description', {})
    if description_obj:
        raw_text = description_obj.get('text', '')
        cleaned_text = raw_text.replace(r'\n', '\n').replace(r'\uD83E\uDDE0', '').strip()
        details["jobInfo"] = cleaned_text

    return details


