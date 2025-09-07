from langgraph.graph import StateGraph, END

from app.nodes.extract_skills import TextConvertorNode
from app.nodes.fetch_matched_skills import FetchMatchedJobsNode
from app.nodes.summarize_results import SummarizationNode
from app.core.llm import get_llm
from app.state.job_state import JobState


class GraphBuilder:
    def __init__(self):
        pass

    def build_job_finder_graph(self):
        llm = get_llm()

        text_convertor_node = TextConvertorNode(llm)
        fetch_matched_job_node = FetchMatchedJobsNode(llm)
        summarization_node = SummarizationNode(llm)

        workflow = StateGraph(JobState)  
        workflow.add_node("byte_to_text", text_convertor_node.extract_text_from_pdf)
        workflow.add_node("text_to_skill", text_convertor_node.extract_skills)
        workflow.add_node("fetch_and_process_jobs", fetch_matched_job_node.fetch_and_process_jobs_node)
        workflow.add_node("summarize_results", summarization_node.summarize_results)

        workflow.set_entry_point("byte_to_text")
        workflow.add_edge("byte_to_text", "text_to_skill")
        workflow.add_edge("text_to_skill", "fetch_and_process_jobs")
        workflow.add_edge("fetch_and_process_jobs", "summarize_results")
        workflow.add_edge("summarize_results", END)

        return workflow.compile()

    def build_direct_search_graph(self):
        """
        Builds a streamlined workflow that starts directly with fetching jobs.
        """
        llm = get_llm()
        fetch_matched_job_node = FetchMatchedJobsNode(llm)
        summarization_node = SummarizationNode(llm)

        workflow = StateGraph(JobState)
        workflow.add_node("fetch_and_process_jobs", fetch_matched_job_node.fetch_and_process_jobs_node)
        workflow.add_node("summarize_results", summarization_node.summarize_results)

        workflow.set_entry_point("fetch_and_process_jobs")
        workflow.add_edge("fetch_and_process_jobs", "summarize_results")
        workflow.add_edge("summarize_results", END)

        return workflow.compile()
