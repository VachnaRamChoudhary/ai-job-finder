import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="AI Job Finder", page_icon="🤖", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def display_results(response_data):
    """Helper function to display the job results and summary."""
    if not response_data:
        st.error("Failed to get a response from the server.")
        return

    summary = response_data.get("summary")
    jobs = response_data.get("jobs")
    skills = response_data.get("skills")
    thought_process = response_data.get("thought_process")

    if thought_process:
        with st.expander("View AI Reasoning"):
            st.markdown("#### AI's Internal Monologue")
            st.info(thought_process)
            st.markdown("---_**Data Used for Analysis**_---")
            if skills:
                st.markdown("**Skills Identified/Used:**")
                st.write(skills)
            if jobs:
                st.markdown("**Jobs Analyzed:**")
                st.json(jobs)

    if summary:
        st.subheader("Your Personalized Summary")
        st.markdown(summary)

    if jobs:
        st.subheader("Top Job Matches")
        df = pd.DataFrame(jobs)
        
        # Clean up and select columns to display
        display_columns = {
            'title': 'Title',
            'company-name': 'Company',
            'formattedJobLocation': 'Location',
            'applyUrl': 'Apply Link'
        }
        
        # Filter dataframe to only include available columns
        columns_to_show = [col for col in display_columns.keys() if col in df.columns]
        df_display = df[columns_to_show].rename(columns=display_columns)

        st.dataframe(
            df_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Apply Link": st.column_config.LinkColumn("Apply", display_text="Apply Here")
            }
        )

        with st.expander("View Full Job Details (JSON)"):
            st.json(jobs)
    else:
        st.info("No jobs were found based on your input.")

# --- UI Layout ---
st.title("🤖 AI-Powered Job Finder")
st.markdown("Get matched with your dream job. Upload your resume or search directly with your skills.")

# --- Sidebar for Navigation ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose your mode", ["Resume Analysis", "Direct Job Search"])

# --- Main Content ---
if app_mode == "Resume Analysis":
    st.header("Resume Analysis")
    st.markdown("Upload your PDF resume, and we'll automatically extract your skills and find the best job matches for you.")

    uploaded_file = st.file_uploader("Choose your resume (PDF only)", type="pdf")

    if uploaded_file is not None:
        with st.spinner('Analyzing your resume and finding jobs... Please wait.'):
            files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
            try:
                response = requests.post(f"{API_BASE_URL}/upload-resume/", files=files, timeout=300)
                if response.status_code == 200:
                    st.success("Analysis complete!")
                    display_results(response.json())
                else:
                    st.error(f"An error occurred: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server: {e}")

elif app_mode == "Direct Job Search":
    st.header("Direct Job Search")
    st.markdown("Enter your skills and preferences to search for jobs directly.")

    with st.form(key='search_form'):
        skills_input = st.text_area("Enter your skills (comma-separated)", "Java, Python, Spring Boot, SQL, Microservices")
        posted_hours = st.number_input("Jobs posted within the last (hours)", min_value=1, value=24)
        size = st.number_input("Number of results to return", min_value=1, max_value=50, value=10)
        page = st.number_input("Page number", min_value=1, value=1)

        submit_button = st.form_submit_button(label='Search for Jobs')

    if submit_button:
        with st.spinner('Searching for the best jobs for you...'):
            skills_list = [skill.strip() for skill in skills_input.split(',')]
            payload = {
                "skills": skills_list,
                "page": page,
                "size": size,
                "posted_hours": posted_hours
            }
            try:
                response = requests.post(f"{API_BASE_URL}/search/", json=payload, timeout=300)
                if response.status_code == 200:
                    st.success("Search complete!")
                    display_results(response.json())
                else:
                    st.error(f"An error occurred: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server: {e}")
