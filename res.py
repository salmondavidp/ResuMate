import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Configure Generative AI with the API key
api_key = os.getenv("GOOGLE_API_KEY")
if api_key is None:
    st.error("API key is not set. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

# Function to get the response from Google's Generative AI model
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from an uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text() or ""
    return text.strip()

# Define the input prompt template
input_prompt = """
Act as a highly skilled ATS with expert knowledge in tech fields like software engineering,
data science, and big data. Analyze the resume against the provided job description,
focusing on keyword matching and competitive job market requirements. 
Provide a detailed evaluation with a match percentage, missing keywords, 
and suggestions for improvement, ensuring accuracy and relevance.

Resume: {text}
Description: {jd}

I want the response in one single string with the structure:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

# Streamlit app starts here
st.set_page_config(page_title="ResuMate", layout="centered")

# Title and description
st.title("ResuMate")
st.subheader("Elevate Your Job Hunt with AI-Driven Resume Insights!")
st.write("""
    Upload your resume and job description for instant AI insights, highlighting improvements and tips to enhance your job prospects!
""")

# Job Description Input Section
st.subheader("📄 Job Description")
jd = st.text_area(
    "Paste the Job Description here", 
    help="Enter the job description you want your resume to be evaluated against."
)

# File Uploader for Resume
st.subheader("📥 Upload Your Resume (PDF Format)")
uploaded_file = st.file_uploader(
    "Upload Your Resume", type="pdf", 
    help="Please upload your resume in PDF format for evaluation."
)

# Submit button with proper validation and response handling
if st.button("Evaluate My Resume"):
    if uploaded_file is not None and jd.strip():
        if uploaded_file.type != "application/pdf":
            st.error("Please upload a valid PDF file.")
        else:
            with st.spinner('Analyzing your resume...'):
                text = input_pdf_text(uploaded_file)
                if not text:
                    st.error("Could not extract any text from the uploaded PDF.")
                else:
                    # Prepare the final prompt to be sent to the model
                    final_prompt = input_prompt.format(text=text, jd=jd)
                    try:
                        # Get the model's response
                        response = get_gemini_response(final_prompt)
                        
                        # Check if response is valid JSON
                        try:
                            evaluation_data = json.loads(response)
                            
                            # Formatting the output
                            match_percentage = evaluation_data.get("JD Match", "N/A")
                            missing_keywords = evaluation_data.get("MissingKeywords", [])
                            profile_summary = evaluation_data.get("Profile Summary", "N/A")

                            # Display the formatted evaluation
                            st.subheader("💡 Your Resume Evaluation")
                            st.write(f"**Match:** {match_percentage}")
                            if missing_keywords:
                                st.write("**Missing Keywords:**")
                                for keyword in missing_keywords:
                                    st.write(f"- {keyword}")
                            else:
                                st.write("**Missing Keywords:** None")
                            st.write(f"**Profile Summary:** {profile_summary}")

                        except json.JSONDecodeError:
                            st.error("Failed to parse response from the AI model. Please try again.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred while contacting the AI model: {str(e)}")
    else:
        st.error("Please provide both a job description and a PDF resume for evaluation.")

# Footer
st.write("---")
st.markdown("Developed by  [SALMONDAVID](https://www.linkedin.com/in/salmondavid/)")
