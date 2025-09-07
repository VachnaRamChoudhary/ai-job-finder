from pydantic import BaseModel
from langgraph.graph import StateGraph, END

from app.nodes.extract_skills import TextConvertorNode
from app.nodes.fetch_matched_skills import FetchMatchedJobsNode
from app.services.scraper import scrape_jobs
from app.core.llm import get_llm
from app.state.job_state import JobState


class GraphBuilder:
    def __init__(self):
        pass

    def build_job_finder_graph(self):
        llm = get_llm()

        text_convertor_node = TextConvertorNode(llm)
        fetch_matched_job_node = FetchMatchedJobsNode(llm)

        workflow = StateGraph(state_schema=JobState)  # ✅ pass schema here
        workflow.add_node("byte_to_text", text_convertor_node.extract_text_from_pdf)
        workflow.add_node("text_to_skill", text_convertor_node.extract_skills)
        workflow.add_node("fetch_match_jobs", fetch_matched_job_node.fetch_matched_jobs)
        workflow.add_node("extract_job_ids", fetch_matched_job_node.fetch_matched_job_ids)
        workflow.add_node("fetch_job_details", fetch_matched_job_node.fetch_matched_jobs_details)

        workflow.set_entry_point("byte_to_text")
        workflow.add_edge("byte_to_text", "text_to_skill")
        workflow.add_edge("text_to_skill", "fetch_match_jobs")
        workflow.add_edge("fetch_match_jobs", "extract_job_ids")
        workflow.add_edge("extract_job_ids", "fetch_job_details")
        workflow.add_edge("fetch_job_details", END)

        return workflow.compile()
