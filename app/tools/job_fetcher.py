"""
This module contains high-level tools for orchestrating complex actions,
like fetching and processing job data from multiple sources.
"""
from typing import List, Dict
from langchain_core.tools import tool

from app.services.linkdin_scraper import (
    get_linkedin_jobs,
    parse_job_data,
    parse_job_id_from_urls,
    get_linkedin_job_details,
    parse_job_json_response,
)
from app.core.logger import get_logger

logger = get_logger(__name__)

@tool
def fetch_and_process_jobs(skills: List[str], job_count: int = 10, start: int = 0, posted_hours: int = 12) -> List[Dict]:
    """
    Fetches, parses, and retrieves details for LinkedIn jobs based on a list of skills.

    This function orchestrates the entire job fetching process:
    1. Searches for jobs using the provided skills.
    2. Parses the initial response to extract job IDs.
    3. Fetches detailed information for each job ID.
    4. Cleans and formats the final job details.

    Args:
        skills: A list of skill keywords to search for.
        job_count: The number of jobs to fetch. Defaults to 10.
        start: The starting index for the job search. Defaults to 0.
        posted_hours: The time window in hours for job postings. Defaults to 12.

    Returns:
        A list of dictionaries, where each dictionary contains the
        detailed information for a matched job.
    """
    logger.info(f"--- Tool: Starting job fetching process for skills: {skills} ---")

    # Step 1: Fetch raw job listings
    raw_jobs = get_linkedin_jobs(skills, count=job_count, start=start, posted_hours=posted_hours)
    if not raw_jobs or "error" in raw_jobs:
        logger.error("Failed to fetch initial job listings from LinkedIn.")
        return []

    # Step 2: Parse job IDs
    job_urls = parse_job_data(raw_jobs)
    job_ids = parse_job_id_from_urls(job_urls)
    if not job_ids:
        logger.warning("No job IDs could be extracted from the search results.")
        return []
    logger.info(f"Successfully extracted {len(job_ids)} job IDs.")

    # Step 3: Fetch details for each job ID
    detailed_jobs = []
    for i, job_id in enumerate(job_ids, 1):
        logger.info(f"Fetching details for job {i}/{len(job_ids)}: {job_id}")
        job_details_raw = get_linkedin_job_details(job_id)
        if job_details_raw and "error" not in job_details_raw:
            extracted_details = parse_job_json_response(job_details_raw)
            detailed_jobs.append(extracted_details)
        else:
            logger.warning(f"Could not fetch details for job ID: {job_id}")

    logger.info(f"Successfully fetched and processed details for {len(detailed_jobs)} jobs.")
    return detailed_jobs
