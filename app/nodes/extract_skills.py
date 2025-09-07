from app.core.logger import get_logger
from app.services.pdf_processer import process_pdf
from app.state.job_state import JobState
import re
import ast


logger = get_logger(__name__)


class TextConvertorNode:
    def __init__(self, llm):
        self.llm = llm

    def extract_text_from_pdf(self, state: JobState) -> JobState:
        logger.info("--- Step: Extracting text from PDF ---")
        text = process_pdf(state.file_bytes)
        state.raw_text = text
        logger.info(f"Successfully extracted {len(text)} characters from PDF.")
        return state

    def extract_skills(self, state: JobState) -> JobState:
        logger.info("--- Step: Extracting skills from raw text ---")
        raw_text = state.raw_text

        from langchain.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert resume analyzer. "
             "Your task is to extract the candidate’s strongest skills from their resume."),
            ("user",
             "From the following resume text:\n\n{raw_text}\n\n"
             "1. Identify the top 5 technical skills.\n"
             "2. Sort these skills by the candidate’s experience level (the most experienced skill first).\n"
             "   If explicit experience is not mentioned, infer based on emphasis and context.\n"
             "3. Extract the candidate’s **total overall professional experience**.\n"
             "4. Return the result as a single Python list of strings, e.g.:\n"
             "   ['Java', 'Spring Boot', 'Python', 'SQL', 'Microservices', '3 years exp']")
        ])

        response = self.llm.invoke(prompt.format(raw_text=raw_text))
        response_content = response.content
        logger.info(f"Raw LLM response for skills: {response_content}")

        # Find the list within the string using regex
        match = re.search(r'\s*(\[.*\])', response_content, re.DOTALL)
        if match:
            list_str = match.group(1)
            try:
                # Safely evaluate the string as a Python literal
                skills_list = ast.literal_eval(list_str)
                # Ensure all items are strings and remove duplicates
                unique_skills = sorted(list(set(map(str, skills_list))))
                state.skills = unique_skills
                logger.info(f"Successfully parsed skills: {unique_skills}")
            except (ValueError, SyntaxError) as e:
                logger.error(f"Failed to parse skills list from LLM response: {e}")
                state.skills = []
        else:
            logger.warning("Could not find a list in the LLM response. Attempting to parse lines.")
            # Fallback: try to parse the content line by line if no list is found
            lines = [line.strip().replace(',', '').replace('"', '').replace("'", '') for line in response_content.split('\n')]
            skills_list = [line for line in lines if line and not line.startswith('<') and not line.startswith('[') and not line.startswith(']')]
            state.skills = sorted(list(set(skills_list)))
            logger.info(f"Fallback parsing extracted skills: {state.skills}")

        return state
