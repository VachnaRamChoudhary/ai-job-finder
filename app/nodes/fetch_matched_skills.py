from app.core.logger import get_logger
from app.tools.job_fetcher import fetch_and_process_jobs
from app.state.job_state import JobState

logger = get_logger(__name__)


class FetchMatchedJobsNode:
    def __init__(self, llm):
        self.llm = llm

    def fetch_and_process_jobs_node(self, state: JobState) -> JobState:
        """
        A graph node that fetches and processes job details using the job_fetcher tool.
        """
        logger.info("--- Step: Fetching and processing jobs ---")
        skills = state.skills
        start_index = state.start
        posted_hours = state.posted_hours
        job_count = state.job_count

        if not skills:
            logger.warning("No skills found in state, skipping job fetch.")
            state.jobs = []
            return state

        # Call the consolidated tool to get the final job list
        tool_input = {
            "skills": skills,
            "job_count": job_count,
            "start": start_index,
            "posted_hours": posted_hours
        }
        detailed_jobs = fetch_and_process_jobs.invoke(tool_input)
        state.jobs = detailed_jobs

        logger.info(f"Finished job fetching process. Found {len(detailed_jobs)} detailed jobs.")
        return state
