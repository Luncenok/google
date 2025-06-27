import streamlit as st
from cvmaker import build_pdf
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from gemini_utils import initialize_gemini, generate_cv_data, rate_cv, apply_suggestions

# Load environment variables from .env file
load_dotenv()

st.set_page_config(layout="wide")

st.title("✨ AI-Powered CV Generator")

# --- Initialize Model ---
model = initialize_gemini()

# --- Functions ---
def get_job_description(url):
    """Fetches and extracts job description from a URL."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        job_description_tags = [
            soup.find(class_="job-description"), soup.find(id="job-description"),
            soup.find(class_="job-details"), soup.find(id="job-details"),
            soup.find("article"),
        ]
        for tag in job_description_tags:
            if tag:
                return tag.get_text(separator='\n', strip=True)
        return soup.find('body').get_text(separator='\n', strip=True)
    except Exception as e:
        st.error(f"An error occurred while fetching the job description: {e}")
        return None

def display_editable_cv(cv_data):
    """Displays the CV data in an editable form."""
    with st.container(border=True):
        st.subheader("Step 2: Edit Your CV")
        
        # Basic Info
        cv_data["name"] = st.text_input("Name", cv_data.get("name", ""))
        cv_data["title"] = st.text_input("Title", cv_data.get("title", ""))
        
        # Contact
        contact = cv_data.get("contact", {})
        c1, c2, c3 = st.columns(3)
        with c1: contact["Email"] = st.text_input("Email", contact.get("Email", ""))
        with c2: contact["LinkedIn"] = st.text_input("LinkedIn", contact.get("LinkedIn", ""))
        with c3: contact["Location"] = st.text_input("Location", contact.get("Location", ""))
        cv_data["contact"] = contact

        # Summary
        cv_data["summary"] = st.text_area("Summary", cv_data.get("summary", ""), height=150)

        # Experience
        st.markdown("##### Experience")
        for i, job in enumerate(cv_data.get("experience", [])):
            with st.expander(f"Job {i+1}: {job.get('title', '')}", expanded=True):
                job["title"] = st.text_input(f"Title {i}", job.get("title", ""))
                job["company"] = st.text_input(f"Company {i}", job.get("company", ""))
                job["date"] = st.text_input(f"Date {i}", job.get("date", ""))
                description = job.get("description", [])
                description_text = "\n".join(description) if isinstance(description, list) else description
                job["description"] = st.text_area(f"Description {i}", description_text, height=150).split("\n")
        
        # Projects
        st.markdown("##### Projects")
        for i, project in enumerate(cv_data.get("projects", [])):
            with st.expander(f"Project {i+1}: {project.get('name', '')}", expanded=True):
                project["name"] = st.text_input(f"Project Name {i}", project.get("name", ""))
                project["date"] = st.text_input(f"Project Date {i}", project.get("date", ""))
                description = project.get("description", [])
                description_text = "\n".join(description) if isinstance(description, list) else description
                project["description"] = st.text_area(f"Project Description {i}", description_text, height=150).split("\n")

    return cv_data

# --- Sidebar ---
with st.sidebar:
    st.header("Your Details")
    user_name = st.text_input("Full Name", "Mateusz Idziejczak")
    user_email = st.text_input("Email", "mateusz.idziejczak@gmail.com")
    user_linkedin = st.text_input("LinkedIn", "linkedin.com/in/mateusz-idziejczak-a2aa65248")
    user_location = st.text_input("Location", "Poznan, Poland")
    user_title = st.text_input("Target Role", "AI & Machine Learning Engineer")
    user_details_text = st.text_area("Paste your raw CV details here", height=300, help="Paste your full, unedited CV here. The AI will use this as source material.")

# --- Main App Layout ---
col1, col2 = st.columns(2)

with col1: # Workspace Column
    with st.container(border=True):
        st.subheader("Step 1: Provide Job Description")
        job_url = st.text_input("Paste the Job Posting URL Here", key="job_url_input")

        if st.button("Scrape Job Description"):
            with st.spinner("Fetching job description..."):
                st.session_state.job_description = get_job_description(job_url)
                # Clear old CV data when new job is scraped
                if 'cv_data' in st.session_state: del st.session_state['cv_data']
                if 'rating' in st.session_state: del st.session_state['rating']
        
        st.session_state.job_description = st.text_area("Scraped Job Description (Editable)", st.session_state.get("job_description", ""), height=200)

    if st.button("Generate Tailored CV", use_container_width=True):
        if not st.session_state.get("job_description"):
            st.warning("Please provide a job description first.")
        else:
            with st.spinner("Generating your tailored CV..."):
                user_details = {"name": user_name, "email": user_email, "linkedin": user_linkedin, "location": user_location, "title": user_title, "raw_cv": user_details_text}
                st.session_state.cv_data = generate_cv_data(model, st.session_state.job_description, user_details)
                if 'rating' in st.session_state: del st.session_state['rating']

    if 'cv_data' in st.session_state:
        st.session_state.cv_data = display_editable_cv(st.session_state.cv_data)

with col2: # AI Analysis Column
    if 'cv_data' in st.session_state:
        with st.container(border=True):
            st.subheader("Step 3: Review and Refine")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Rate CV", use_container_width=True):
                    with st.spinner("Rating your CV..."):
                        st.session_state.rating = rate_cv(model, st.session_state.job_description, st.session_state.cv_data)
            with b2:
                if 'rating' in st.session_state:
                    if st.button("Apply Suggestions", use_container_width=True):
                        with st.spinner("Applying suggestions..."):
                            st.session_state.cv_data = apply_suggestions(model, st.session_state.cv_data, st.session_state.rating)
                            st.rerun()
            with b3:
                if st.button("Generate PDF", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        pdf_file_name = f"{st.session_state.cv_data['name'].replace(' ', '_')}_CV.pdf"
                        build_pdf(pdf_file_name, st.session_state.cv_data)
                        with open(pdf_file_name, "rb") as pdf_file:
                            st.download_button(label="Download PDF", data=pdf_file, file_name=pdf_file_name, mime="application/octet-stream", use_container_width=True)

        if 'rating' in st.session_state:
            with st.container(border=True):
                st.subheader("AI Feedback")
                st.markdown(st.session_state.rating)