# ✨ AI-Powered CV Generator

This Streamlit application leverages the power of Google's Gemini AI to help users create professional, tailored CVs that are optimized for specific job descriptions. It provides a complete workflow from scraping a job posting to generating a polished PDF, with AI-driven feedback and editing at every step.

## Features

*   **Intelligent Job Scraping**: Paste a URL to a job posting, and the application will automatically extract the relevant job description text.
*   **Editable Job Description**: A manual override allows you to clean up the scraped text, ensuring the AI has the highest quality input.
*   **AI-Powered CV Generation**: Based on your raw CV details and the job description, Gemini generates a tailored CV in a structured JSON format, using the STAR method for impact-oriented descriptions.
*   **Comprehensive CV Editor**: A dynamic, interactive form allows you to edit every field of the generated CV. You can add or remove entries for experience, projects, publications, and more.
*   **Expert AI Rating**: Get a score and detailed, actionable feedback on your CV from an AI persona acting as an expert technical recruiter. The feedback focuses on relevance, impact (STAR method), and clarity.
*   **One-Click Suggestions**: Automatically apply the AI's suggestions to your CV with a single button click.
*   **PDF Generation**: Create a professional, well-formatted PDF of your final CV at any time.

## Tech Stack

*   **Frontend**: Streamlit
*   **AI**: Google Gemini Pro
*   **PDF Generation**: ReportLab
*   **Web Scraping**: Requests, BeautifulSoup4
*   **Dependencies**: `uv`, `python-dotenv`

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment:**
    This project uses `uv` for fast dependency management.
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

5.  **Set up your API Key:**
    Create a file named `.env` in the root of the project directory and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Fill in your details:**
    In the sidebar, enter your name, contact information, target role, and paste your raw, unedited CV content.

3.  **Scrape the Job Description:**
    Paste the URL of a job posting into the main text box and click "Scrape Job Description". Review and edit the scraped text for accuracy.

4.  **Generate the CV:**
    Click "Generate Tailored CV". The AI will create a new version of your CV in the editor.

5.  **Edit and Refine:**
    Manually edit any field in the CV editor.

6.  **Get AI Feedback:**
    Click "Rate CV" to get a score and suggestions. To automatically apply the feedback, click "Apply Suggestions".

7.  **Generate PDF:**
    Once you are satisfied, click "Generate PDF" to download your final CV.

## Future Work

This application is a powerful tool, but there are several features that could make it even better:

*   **Save/Load Sessions**: Implement a feature to save the current state (job description, CV data, user details) to a local file (e.g., a `.json` or `.pkl` file). This would allow users to manage multiple CV versions for different jobs without starting over each time.
*   **Advanced Text Editor**: Replace the standard `st.text_area` for descriptions with a rich text editor that supports basic formatting like bold, italics, and bullet points.
*   **Customizable PDF Templates**: Allow users to choose from several different PDF layouts and color schemes to personalize their final CV.
*   **Deployment**: Deploy the application to a service like Streamlit Community Cloud or Hugging Face Spaces so it can be easily accessed and shared online.
*   **Improved Error Handling**: Add more granular error handling, especially for web scraping, to guide the user if a site is difficult to parse.
*   **Direct PDF Editing**: Explore libraries that could allow for direct manipulation or annotation of the generated PDF within the app.
