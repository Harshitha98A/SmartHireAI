import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import pandas as pd
import json
import re
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import openpyxl
from openpyxl.worksheet.hyperlink import Hyperlink
 
# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
 
# Gemini response with timeout handling
def get_gemini_response(input, timeout=10, retries=3, delay=5):
    def generate_content():
        client = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = client.generate_content(input)
        return response.text
 
    for attempt in range(retries):
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(generate_content)
                return future.result(timeout=timeout)
        except TimeoutError:
            st.error(f"Request timed out after {timeout} seconds on attempt {attempt + 1}. Retrying...")
        except Exception as e:
            st.error(f"Error generating response from Gemini on attempt {attempt + 1}: {e}. Retrying...")
 
        # Delay before retry
        time.sleep(delay)
 
    # If all retries fail, return None
    st.error(f"Failed to generate a response after {retries} attempts. Please try again later.")
    return None
 
# Extract text from PDF files
def input_pdf_text(uploaded_file):
    text = ""
    try:
        reader = pdf.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except pdf.errors.PdfReadError:
        text = "Error: Corrupt or unsupported PDF file."
    except Exception as e:
        text = f"Error: {str(e)}"
    return text

    
#def input_pdf_text(uploaded_file):
    
    #reader = pdf.PdfReader(uploaded_file)
    #text = ""
   # for page in range(len(reader.pages)):
   #     page_text = reader.pages[page].extract_text()
   #     if page_text:
   #         text += str(page_text) + "\n"
   # return text
 
# Create prompt for Gemini
def create_prompt(resumes, jd, additional_notes):
    input_prompt = f"""
    You are a specialized Applicant Tracking System (ATS) analyzing candidates for a Talent Acquisition Specialist role. Please evaluate the provided resume against the job description and additional notes, and output only in strict JSON format without additional text.
    Please provide the "JD Match" as a percentage whole number representing how closely the resume aligns with the job description (e.g., 70, 85, 90).  
    Also, include specific "Contextual Alignment Comments" in strictly 500 characters explaining the reasons behind the match percentage and highlighting the candidate's strengths and weaknesses.
    Additional considerations based on notes provided: {additional_notes}
    ### Input:
    - Resume: {resumes}
    - Job Description: {jd}
 
    ### Required JSON Output:
    {{
        "Rank of the resume": "",
        "JD Match": "XX",
        "Contextual Alignment Comments": "Brief summary of the candidate's fit for the job role in strictly less than 500 characters"
    }}
    Note: Return only this JSON response format with field names exactly as specified.
    """
    return input_prompt
 
# Streamlit app
st.title("Smart ATS")
st.text("Shortlist Candidates")
 
# Job Description input
jd = st.text_area("Paste the Job Description")
if not jd:
    st.warning("Please enter a Job Description.")
 
# Additional details input
additional_notes = st.text_area("Enter any additional details to consider (optional)")
 
if jd:
    uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True)
    submit = st.button("Submit")
 
    if submit:
        if uploaded_files:
            results = []
            resume_names = []
            total_files = len(uploaded_files)
            progress_bar = st.progress(0)
 
            for idx, uploaded_file in enumerate(uploaded_files):
                resume_name = uploaded_file.name
                resume_names.append(resume_name)
 
                st.text(f"Analyzing {resume_name}...")
                # Extract text and create prompt
                text = input_pdf_text(uploaded_file)
                prompt = create_prompt(text, jd, additional_notes)
 
                # Generate Gemini response with timeout
                response = get_gemini_response(prompt, timeout=10)
 
                if response:
                    try:
                        # Try to parse the response as JSON
                        response_data = json.loads(response)
                        results.append({
                            "Resume_name": resume_name,
                            "Rank of the resume": "",
                            "JD Match": response_data.get("JD Match", "0"),
                            "Contextual Alignment Comments": response_data.get("Contextual Alignment Comments", "No comments provided."),
                        })
                    except json.JSONDecodeError:
                        # Handle non-JSON response by extracting numeric match value using regex
                        match_percentage = re.search(r'\b\d{1,3}\b', response)
                        jd_match = match_percentage.group(0) if match_percentage else "0"

                        results.append({
                        "Resume_name": resume_name,
                        "Rank of the resume": "",
                        "JD Match": jd_match,
                        "Contextual Alignment Comments": response.strip()[:650]  # Limit to 500 chars to prevent long errors -> increasing to 650 on 3/20
                        })
                        st.warning(f"Received non-JSON response for {resume_name}. Extracted JD Match: {jd_match}.")
                else:
                    st.error(f"No response generated for {resume_name}.")
                    results.append({
                        "Resume_name": resume_name,
                        "Rank of the resume": "",
                        "JD Match": "0",
                        "Contextual Alignment Comments": "No response generated.",
                     })
 
                progress = (idx + 1) / total_files
                progress_bar.progress(progress)
                time.sleep(2)
 
            # Convert JD Match to numeric values
            for result in results:
                jd_match = result.get("JD Match", "0")
                try:
                    match_percentage = float(jd_match.strip('%')) if isinstance(jd_match, str) and '%' in jd_match else float(jd_match)
                    result["JD Match"] = match_percentage
                except (ValueError, TypeError):
                    result["JD Match"] = 0.0
 
            # Sort results by JD Match and assign ranks
            results = sorted(results, key=lambda x: x["JD Match"], reverse=True)
            for rank, result in enumerate(results, start=1):
                result["Rank of the resume"] = rank
 
            # Create DataFrame
            df = pd.DataFrame(results)
 
            # Add file location column
            #file_locations = [f"file:///{os.path.abspath(uploaded_file.name)}" for uploaded_file in uploaded_files]
            #df["File Location"] = file_locations
 
            # Reorder columns
            df = df[
                [
                    "Rank of the resume",
                    "Resume_name",
                    "JD Match",
                    "Contextual Alignment Comments",
                ]
            ]
 
            # Save results to Excel
            excel_file = f"evaluation_results.xlsx"
 
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
 
                '''# Add hyperlinks
                ws = writer.sheets['Results']
                for row in ws.iter_rows(min_row=2, min_col=df.columns.get_loc("File Location") + 1, max_col=df.columns.get_loc("File Location") + 1):
                    for cell in row:
                        file_path = cell.value
                        cell.hyperlink = file_path
                        cell.style = "Hyperlink"  # Apply the Hyperlink style'''
 
            # Download button
            with open(excel_file, "rb") as f:
                st.download_button(
                    "Download Evaluation Results",
                    f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
# fixing the bad message error which was being recieved in the 23rd.
#fixed non json response 3/14 and updated gemini updates on version nomenclature