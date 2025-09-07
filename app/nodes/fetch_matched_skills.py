from app.core.logger import get_logger
from app.services.linkdin_scraper import get_linkedin_jobs, parse_job_data, parse_job_id_from_urls, \
    get_linkedin_job_details, parse_job_json_response
from app.state.job_state import JobState


logger = get_logger(__name__)


class FetchMatchedJobsNode:
    def __init__(self, llm):
        self.llm = llm

    def fetch_matched_jobs(self, state: JobState) -> JobState:
        logger.info("--- Step: Fetching matched jobs from LinkedIn ---")
        skills = state.skills
        logger.info(f"Searching for jobs with skills: {skills}")
        fetched_raw_jobs = get_linkedin_jobs(skills, 10, 0)
        state.raw_jobs = fetched_raw_jobs
        logger.info(f"Received {len(fetched_raw_jobs.get('data', {}).get('data', {}).get('jobsDashJobCardsBySemanticSearch', {}).get('elements', []))} raw job results.")
        return state

    def fetch_matched_job_ids(self, state: JobState) -> JobState:
        logger.info("--- Step: Extracting job IDs from raw job data ---")
        raw_jobs = state.raw_jobs
        job_lists = parse_job_data(raw_jobs)
        job_ids = parse_job_id_from_urls(job_lists)
        state.job_ids = job_ids
        logger.info(f"Extracted {len(job_ids)} job IDs: {job_ids}")
        return state

    def fetch_matched_jobs_details(self, state: JobState) -> JobState:
        logger.info("--- Step: Fetching detailed information for each job ID ---")
        job_ids = state.job_ids

        dic_list_job_info = []
        for i, job_id in enumerate(job_ids, 1):
            logger.info(f"Fetching details for job {i}/{len(job_ids)}: {job_id}")
            job_info = get_linkedin_job_details(job_id)
            extracted_job_info = parse_job_json_response(job_info)
            dic_list_job_info.append(extracted_job_info)

        state.jobs = dic_list_job_info
        logger.info(f"Successfully fetched details for {len(dic_list_job_info)} jobs.")
        return state
