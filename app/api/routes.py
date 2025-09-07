from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Annotated

from app.graph.workflow import GraphBuilder
from app.state.job_state import JobState
from app.models.schemas import JobSearchRequest

router = APIRouter()


@router.post("/upload-resume/")
async def upload_resume_and_find_jobs(file: Annotated[UploadFile, File(description="The PDF resume file to process.")]):
    """
    Accepts a PDF resume, runs it through the job-finding workflow,
    and returns the final state with matched jobs.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF document."
        )

    try:
        pdf_bytes = await file.read()

        # 1. Initialize the graph builder and compile the workflow
        graph_builder = GraphBuilder()
        workflow = graph_builder.build_job_finder_graph()

        # 2. Set up the initial state for the graph
        # The graph starts with bytes and will fill in the other fields.
        initial_state = JobState(file_bytes=pdf_bytes)

        # 3. Invoke the workflow and get the final result
        final_state = workflow.invoke(initial_state)

        # 4. Create a serializable response, excluding the raw file bytes
        # The final state is a dict, so we just remove the key
        final_state.pop('file_bytes', None)

        return final_state

    except ValueError as e:
        # Catches errors from PDF processing or other validation
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # General error handler for unexpected issues
        print(f"An unexpected error occurred: {e}") # For debugging
        raise HTTPException(status_code=500, detail="An unexpected error occurred on the server.")


@router.post("/search/")
async def direct_job_search(request: JobSearchRequest):
    """
    Accepts a list of skills and other parameters to directly search for jobs.
    """
    try:
        # Calculate the start index for pagination from the page number and size
        start_index = (request.page - 1) * request.size

        # 1. Initialize the graph builder and compile the direct search workflow
        graph_builder = GraphBuilder()
        workflow = graph_builder.build_direct_search_graph()

        # 2. Set up the initial state for the graph from the request
        initial_state = JobState(
            skills=request.skills,
            start=start_index,
            job_count=request.size,
            posted_hours=request.posted_hours
        )

        # 3. Invoke the workflow and get the final result
        final_state = workflow.invoke(initial_state)

        return final_state

    except Exception as e:
        # General error handler for unexpected issues
        print(f"An unexpected error occurred: {e}") # For debugging
        raise HTTPException(status_code=500, detail="An unexpected error occurred on the server.")
