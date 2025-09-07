import re
from app.core.logger import get_logger
from app.state.job_state import JobState
from langchain.prompts import ChatPromptTemplate

logger = get_logger(__name__)


class SummarizationNode:
    def __init__(self, llm):
        self.llm = llm

    def summarize_results(self, state: JobState) -> JobState:
        """
        Analyzes the fetched jobs against the user's skills and generates a summary.
        """
        logger.info("--- Step: Summarizing job results ---")
        skills = state.skills
        jobs = state.jobs

        if not jobs:
            logger.info("No jobs to summarize, skipping.")
            state.summary = "No jobs were found matching your skills."
            return state

        # Create a simplified text representation of the jobs for the LLM
        job_details_for_prompt = []
        for job in jobs:
            details = (
                f"- Title: {job.get('title')}\n"
                f"  Company: {job.get('company-name')}\n"
                f"  Location: {job.get('formattedJobLocation')}\n"
                f"  LinkedIn URL: {job.get('linkedin_url')}\n"
                f"  Description Snippet: {job.get('jobInfo', '')[:200]}...\n"
            )
            job_details_for_prompt.append(details)

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert career advisor. Your task is to analyze a list of job opportunities "
             "based on a candidate's skills. First, think step-by-step about which jobs are the best fit and why. "
             "Enclose this reasoning in <thinking> and </thinking> tags. "
             "After your reasoning, provide a brief, encouraging summary for the candidate that highlights the top 2-3 most relevant jobs. "
             "For each recommended job, include its title, company, linkedin_url and a direct link to the job posting, using provided details."
             "Address the candidate directly in the final summary."
             ),
            ("user",
             "Here are my skills: {skills}\n\n"
             "And here are the job listings you found for me:\n"
             "{job_details}\n\n"
             "Please provide your thinking process and then the final summary."
             )
        ])

        chain = prompt | self.llm
        response_content = chain.invoke({
            "skills": ", ".join(skills),
            "job_details": "\n".join(job_details_for_prompt)
        }).content

        # Parse the thinking block and the summary
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_content, re.DOTALL)
        thought_process = thinking_match.group(1).strip() if thinking_match else ""

        # The summary is whatever is left after the thinking block
        summary = re.sub(r'<thinking>.*?</thinking>', '', response_content, flags=re.DOTALL).strip()

        state.thought_process = thought_process
        state.summary = summary
        logger.info(f"Generated thought process: {thought_process}")
        logger.info(f"Generated summary: {summary}")

        return state
