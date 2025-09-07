# AI Job Finder

Production-ready AI workflow using LangGraph, LangChain, Groq, and LangServe to parse a resume (PDF), generate a search query, fetch jobs (Adzuna API with mock fallback), and return the top matched job.

## Features
- Parse resume PDF with `pypdf`.
- Derive concise job search query using Groq LLM.
- Fetch jobs via Adzuna Jobs API (or mock fallback if keys not set).
- Rank and return the single best match as JSON.
- Exposed via FastAPI + LangServe.
- File upload endpoint to trigger the pipeline.
- Pytest tests with monkeypatched tools.

## Requirements
- Python 3.10+
- See `requirements.txt`

## Environment
Create `.env` with:

```
# Groq LLM
GROQ_API_KEY=your_groq_key

# LangSmith (optional tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key

# Adzuna Jobs API (optional, enables real job search)
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
ADZUNA_COUNTRY=us
```

## Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```
uvicorn app.server:app --reload
```

- LangServe route: `POST /resume-matcher/invoke`
  - Body: `{ "input": { "pdf_path": "/absolute/or/relative/path/to/resume.pdf" } }`
- Upload route: `POST /upload-resume` (multipart/form-data)
  - Form file field: `file` (PDF only)

Example cURL (invoke):
```
curl -s http://127.0.0.1:8000/resume-matcher/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"pdf_path": "samples/resume.pdf"}}' | jq
```

Example cURL (upload):
```
curl -s -F "file=@samples/resume.pdf" http://127.0.0.1:8000/upload-resume | jq
```

## Tests
Run tests:
```
pytest -q
```

## Project Structure
- `app/agents.py` — Groq LLM init, tools: `parse_resume_pdf`, `search_linkedin_jobs` (Adzuna + mock fallback)
- `app/core.py` — LangGraph pipeline nodes and compiled runnable `app`
- `app/server.py` — FastAPI app, LangServe route, upload endpoint
- `tests/` — pytest-based unit tests

## Notes
- The Adzuna integration is a compliant, production-ready data source alternative to scraping LinkedIn.
- For stricter JSON, consider adding Pydantic models for `top_match` and validating LLM output.
- To switch to another jobs API, update `search_linkedin_jobs` in `app/agents.py`.
