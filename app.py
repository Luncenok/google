import streamlit as st
from cvmaker import build_pdf
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from gemini_utils import initialize_gemini, generate_cv_data, rate_cv, apply_suggestions
import os
import json
from template_config import TEMPLATES

# Load environment variables from .env file
load_dotenv()

st.set_page_config(layout="wide")

st.title("✨ AI-Powered CV Generator")

# --- Constants ---
PROFILES_DIR = "profiles"

# --- Profile Functions ---
def load_profiles():
    """Loads all profiles from the profiles directory."""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)
    profiles = {}
    for filename in os.listdir(PROFILES_DIR):
        if filename.endswith(".json"):
            profile_name = os.path.splitext(filename)[0]
            with open(os.path.join(PROFILES_DIR, filename), 'r') as f:
                profiles[profile_name] = json.load(f)
    return profiles

def save_profile(profile_name, data):
    """Saves a profile to a JSON file."""
    if not profile_name:
        st.error("Profile name cannot be empty.")
        return
    file_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    st.success(f"Profile '{profile_name}' saved!")


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
    """Displays the CV data in a fully editable form with add/remove buttons."""
    with st.container(border=True):
        st.subheader("Step 2: Edit Your CV")

        # --- Helper function for dynamic list editing ---
        def manage_list_items(section_title, section_data, template_item):
            st.markdown(f"##### {section_title}")
            
            items_to_remove = []
            for i, item in enumerate(section_data):
                # Use a more robust key for the expander title
                expander_title = item.get("title", item.get("name", item.get("degree", f"Item {i+1}")))
                with st.expander(f"{section_title} {i+1}: {expander_title}", expanded=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        for key, value in template_item.items():
                            # Special handling for description field
                            if key == "description":
                                # Check if description is a list or a single string
                                current_desc = item.get(key, [])
                                if isinstance(current_desc, list):
                                    # Join list into a single string for the text_area
                                    display_text = "\\n".join(current_desc)
                                else:
                                    # If it's already a string, use it directly
                                    display_text = current_desc
                                
                                # The output of text_area is always a string. We split it back into a list.
                                item[key] = st.text_area(f"{key.capitalize()} {i}", display_text, key=f"{section_title}_{i}_{key}", height=150).split('\\n')
                            else:
                                item[key] = st.text_input(f"{key.capitalize()} {i}", item.get(key, ""), key=f"{section_title}_{i}_{key}")
                    with c2:
                        if st.button(f"Remove", key=f"remove_{section_title}_{i}", use_container_width=True):
                            items_to_remove.append(i)
            
            for i in sorted(items_to_remove, reverse=True):
                section_data.pop(i)
                st.rerun()

            if st.button(f"Add {section_title}", key=f"add_{section_title}", use_container_width=True):
                section_data.append(template_item.copy())
                st.rerun()

        # --- Form Fields ---
        cv_data["name"] = st.text_input("Name", cv_data.get("name", ""))
        cv_data["title"] = st.text_input("Title", cv_data.get("title", ""))
        
        contact = cv_data.get("contact", {})
        c1, c2, c3 = st.columns(3)
        with c1: contact["Email"] = st.text_input("Email", contact.get("Email", ""))
        with c2: contact["LinkedIn"] = st.text_input("LinkedIn", contact.get("LinkedIn", ""))
        with c3: contact["Location"] = st.text_input("Location", contact.get("Location", ""))
        cv_data["contact"] = contact

        cv_data["summary"] = st.text_area("Summary", cv_data.get("summary", ""), height=150)

        # --- Dynamic Sections ---
        manage_list_items("Experience", cv_data.get("experience", []), {"title": "", "company": "", "date": "", "location": "", "description": ""})
        manage_list_items("Project", cv_data.get("projects", []), {"name": "", "date": "", "description": ""})
        manage_list_items("Publication", cv_data.get("publications", []), {"title": "", "journal": "", "date": "", "doi": ""})
        manage_list_items("Education", cv_data.get("education", []), {"degree": "", "institution": "", "date": ""})
        manage_list_items("Language", cv_data.get("languages", []), {"name": "", "label": ""})
        
        # Awards are simple strings, not objects, so handle them differently.
        st.markdown("##### Awards")
        awards = cv_data.get("awards", [])
        for i in range(len(awards)):
            awards[i] = st.text_input(f"Award {i+1}", awards[i], key=f"award_{i}")
        if st.button("Add Award", use_container_width=True):
            awards.append("")
            st.rerun()
        cv_data["awards"] = awards

        # Skills
        st.markdown("##### Skills")
        skills = cv_data.get("skills", {})
        if isinstance(skills, dict):
            skills_text = "\n".join([f"{category}: {', '.join(skill_list)}" for category, skill_list in skills.items()])
            edited_skills_text = st.text_area("Skills (Category: Skill1, Skill2...)", skills_text, height=150)
            new_skills = {}
            for line in edited_skills_text.split("\n"):
                if ":" in line:
                    category, skill_part = line.split(":", 1)
                    new_skills[category.strip()] = [s.strip() for s in skill_part.split(",")]
            cv_data["skills"] = new_skills
        elif isinstance(skills, list):
            skills_text = ", ".join(skills)
            edited_skills_text = st.text_area("Skills", skills_text, height=100)
            cv_data["skills"] = [s.strip() for s in edited_skills_text.split(",")]

    return cv_data

# --- Sidebar ---
with st.sidebar:
    st.header("CV Customization")
    template_options = list(TEMPLATES.keys())
    selected_template = st.selectbox("Choose a CV Template", template_options)

    st.header("User Profiles")
    profiles = load_profiles()
    profile_names = list(profiles.keys()) + ["Create New Profile"] 
    
    selected_profile_name = st.selectbox("Select a Profile", profile_names)

    if selected_profile_name == "Create New Profile":
        current_profile = {}
    else:
        current_profile = profiles[selected_profile_name]

    st.header("Your Details")
    user_name = st.text_input("Full Name", current_profile.get("user_name", "Mateusz Idziejczak"))
    user_email = st.text_input("Email", current_profile.get("user_email", "mateusz.idziejczak@gmail.com"))
    user_linkedin = st.text_input("LinkedIn", current_profile.get("user_linkedin", "linkedin.com/in/mateusz-idziejczak-a2aa65248"))
    user_location = st.text_input("Location", current_profile.get("user_location", "Poznan, Poland"))
    user_title = st.text_input("Target Role", current_profile.get("user_title", "AI & Machine Learning Engineer"))
    user_details_text = st.text_area("Paste your raw CV details here", current_profile.get("user_details_text", ""), height=300, help="Paste your full, unedited CV here. The AI will use this as source material.")

    new_profile_name = st.text_input("Enter new profile name to save")
    if st.button("Save Profile"):
        profile_data = {
            "user_name": user_name,
            "user_email": user_email,
            "user_linkedin": user_linkedin,
            "user_location": user_location,
            "user_title": user_title,
            "user_details_text": user_details_text
        }
        save_profile(new_profile_name, profile_data)


# --- Main App Layout ---
col1, col2 = st.columns(2)

with col1: # Workspace Column
    with st.container(border=True):
        st.subheader("Step 1: Provide Job Descriptions")
        job_urls_text = st.text_area("Paste the Job Posting URLs (one per line)", height=100)
        if st.button("Scrape Job Descriptions"):
            with st.spinner("Fetching job descriptions..."):
                urls = [line.strip() for line in job_urls_text.splitlines() if line.strip()]
                st.session_state.job_urls = urls
                descriptions = [get_job_description(url) or "" for url in urls]
                st.session_state.job_descriptions = descriptions
                # Clear old CV data and ratings
                if 'cv_data' in st.session_state: del st.session_state['cv_data']
                if 'rating' in st.session_state: del st.session_state['rating']
        # Display each fetched job description for editing without directly modifying session_state
        for i, desc in enumerate(st.session_state.get('job_descriptions', [])):
            key = f"job_desc_{i}"
            # Use existing session_state value if present, else default to desc
            current = st.session_state.get(key, desc)
            st.text_area(f"Job Description {i+1}", value=current, key=key, height=150)

    if st.button("Generate Tailored CVs & PDFs", use_container_width=True):
        descriptions = [st.session_state.get(f"job_desc_{i}") for i in range(len(st.session_state.get('job_descriptions', [])))]
        if not descriptions:
            st.warning("Please provide at least one job description first.")
        else:
            with st.spinner("Generating your tailored CVs and PDFs..."):
                user_details = {"name": user_name, "email": user_email, "linkedin": user_linkedin, "location": user_location, "title": user_title, "raw_cv": user_details_text}
                generated = []
                for i, desc_text in enumerate(descriptions):
                    cv = generate_cv_data(model, desc_text, user_details)
                    pdf_name = f"{user_name.replace(' ', '_')}_CV_{i+1}.pdf"
                    build_pdf(pdf_name, cv, selected_template)
                    generated.append({"cv_data": cv, "pdf_name": pdf_name})
                # Store generated CVs for persistent download buttons and analysis
                st.session_state.generated_cvs = generated
                # For analysis, use the first CV
                if generated:
                    st.session_state.cv_data = generated[0]["cv_data"]
                if 'rating' in st.session_state:
                    del st.session_state['rating']

    # Show persistent download buttons for generated PDFs
    if st.session_state.get('generated_cvs'):
        for idx, item in enumerate(st.session_state.generated_cvs):
            with open(item['pdf_name'], 'rb') as pdf_file:
                st.download_button(label=f"Download PDF for Job {idx+1}", data=pdf_file, file_name=item['pdf_name'], mime="application/octet-stream", use_container_width=True)

with col2: # AI Analysis Column
    # Allow rating for each generated CV
    if st.session_state.get('generated_cvs'):
        with st.container(border=True):
            st.subheader("Step 3: Review and Refine")
            for idx, item in enumerate(st.session_state.generated_cvs):
                if st.button(f"Rate Job {idx+1}", key=f"rate_{idx}", use_container_width=True):
                    with st.spinner(f"Rating CV for Job {idx+1}..."):
                        desc = st.session_state.job_descriptions[idx]
                        rating = rate_cv(model, desc, item['cv_data'])
                        ratings = st.session_state.get('ratings', {})
                        ratings[idx] = rating
                        st.session_state['ratings'] = ratings
            # Display ratings for each job
            if st.session_state.get('ratings'):
                st.subheader("AI Feedback")
                for idx, rating in st.session_state['ratings'].items():
                    st.markdown(f"**Job {idx+1}:**\n{rating}")
