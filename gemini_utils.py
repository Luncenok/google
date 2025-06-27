import os
import json
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from cvmaker import CV_DATA

def initialize_gemini():
    """Initializes the Gemini model."""
    api_key = None
    try:
        # Try getting API key from Streamlit secrets first (for deployment)
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fallback to environment variable (for local development)
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("GEMINI_API_KEY not found. Please add it to your .env file or Streamlit secrets.", icon="🚨")
        st.stop()

def generate_cv_data(model, job_description, user_details):
    """Generates CV data using Gemini AI in JSON mode."""
    prompt = f"""
    You are an expert Technical Recruiter and professional CV writer. Your task is to create a new, tailored CV in JSON format based on the provided raw CV details and a specific job description.

    **Your Goal:** Rewrite and enhance the user's raw details to be a perfect match for the target job. Use the **STAR method (Situation, Task, Action, Result)** to rephrase experience and project descriptions, focusing on quantifiable achievements and impact.

    **Instructions:**
    1.  **Analyze the Job Description:** Identify the key skills, technologies, and responsibilities required.
    2.  **Analyze the Raw CV:** Understand the user's background and experience.
    3.  **Rewrite and Tailor:**
        *   Create a powerful **summary** that directly addresses the job description and highlights the user's most relevant qualifications.
        *   Rephrase the **experience** and **projects** bullet points to be action-oriented and results-driven. Use the STAR method. Quantify results wherever possible (e.g., "Increased performance by 30%" or "Reduced processing time from 10 minutes to 2 minutes").
        *   Select and prioritize **skills** that are most relevant to the job description.
    4.  **Format as JSON:** The final output must be a valid JSON object following the provided structure. Do not include any text or markdown outside of the JSON object.

    **JSON Structure to Follow:**
    {json.dumps(CV_DATA, indent=2)}

    ---
    **Job Description:**
    {job_description}

    **User's Raw CV Details:**
    {user_details}
    """
    try:
        generation_config = GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        st.error(f"An error occurred while decoding the JSON from the model: {e}")
        st.text_area("Model's Raw Response (that caused the error)", response.text)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def rate_cv(model, job_description, cv_data):
    """Rates the CV against the job description and provides suggestions."""
    prompt = f"""
    You are an expert Technical Recruiter and Career Coach with 15 years of experience hiring for top-tier tech companies.
    Your task is to provide a critical and constructive evaluation of the provided CV against the given Job Description.

    Use the **STAR method (Situation, Task, Action, Result)** as your primary framework for evaluating the 'experience' and 'projects' sections. The best CVs demonstrate impact with quantifiable results.

    Analyze the CV based on the following criteria:
    1.  **Relevance:** How closely do the skills and experiences match the key requirements in the job description?
    2.  **Impact:** Does the CV use the STAR method to show quantifiable achievements instead of just listing responsibilities?
    3.  **Clarity and Keywords:** Is the CV easy to read? Does it contain the right keywords from the job description?

    Provide your feedback in the following format:

    **Overall Score:** [Your score out of 100]

    **Score Justification:** [A brief, 1-2 sentence explanation for your score.]

    **Strengths:**
    *   [Bullet point highlighting a specific strength and why it's good.]
    *   [Another bullet point.]

    **Areas for Improvement:**
    *   [A specific, actionable suggestion. For example: "In the 'Software Engineer' role, rephrase the first bullet point using the STAR method. Instead of 'Engineered and deployed a web application,' try 'Increased volunteer data submission by 40% by engineering and deploying a full-stack web application for 2500+ users.'"]
    *   [Another actionable suggestion.]

    ---
    **Job Description:**
    {job_description}

    **CV:**
    {json.dumps(cv_data, indent=2)}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while rating the CV: {e}")
        return None

def apply_suggestions(model, cv_data, suggestions):
    """Applies the suggestions to the CV data using Gemini AI."""
    prompt = f"""
    You are an expert CV editor. Your task is to rewrite the provided CV data based on the given suggestions.
    The output should be a valid JSON object that follows the original structure.

    Original CV Data:
    {json.dumps(cv_data, indent=2)}

    Suggestions:
    {suggestions}

    Please provide the rewritten CV data in the same JSON format.
    """
    try:
        generation_config = GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        st.error(f"An error occurred while decoding the JSON from the model: {e}")
        st.text_area("Model's Raw Response (that caused the error)", response.text)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None