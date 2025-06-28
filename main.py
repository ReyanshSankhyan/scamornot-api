import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from typing import Optional, Union

import io
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI with API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Function to generate content using Gemini Vision Pro
async def generate_gemini_content(prompt: str, image_data: Optional[bytes] = None, text_input: Optional[str] = None):
    try:
        # Open the image using Pillow
        model = genai.GenerativeModel('gemini-1.5-flash') # Updated model name
        contents = [prompt]
        if image_data:
            img = Image.open(io.BytesIO(image_data))
            contents.append(img)
        if text_input:
            contents.append(text_input)
        response = model.generate_content(contents)
        # Assuming the response text is in the format 'Assessment: ...\nReasoning: ...'
        text_response = response.text
        assessment = "N/A"
        reasoning = "N/A"
        confidence_score = 0

        if "Assessment:" in text_response and "Reasoning:" in text_response and "ConfidenceScore:" in text_response:
            parts = text_response.split("Reasoning:", 1)
            assessment_part = parts[0].replace("Assessment:", "").strip()
            remaining_parts = parts[1].split("ConfidenceScore:", 1)
            reasoning_part = remaining_parts[0].strip()
            try:
                confidence_score_part = int(remaining_parts[1].strip())
                confidence_score = confidence_score_part
            except ValueError:
                pass # Keep default 0 if parsing fails
            assessment = assessment_part
            reasoning = reasoning_part
        elif "Assessment:" in text_response:
            assessment = text_response.replace("Assessment:", "").strip()
        elif "Reasoning:" in text_response:
            reasoning = text_response.replace("Reasoning:", "").strip()
        else:
            # Fallback if the expected format is not found
            assessment = "Could not parse assessment."
            reasoning = text_response

        return {"Assessment": assessment, "Reasoning": reasoning, "ConfidenceScore": confidence_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content from Gemini: {e}")

@app.post("/api/v1/check-malicious-text")
async def check_malicious_text(text: Optional[str] = None, file: Optional[UploadFile] = File(None)):
    if not text and not file:
        raise HTTPException(status_code=400, detail="Either 'text' or 'file' must be provided.")

    image_data = None
    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        image_data = await file.read()

    prompt = (
        "Analyze the provided text or text within the image for malicious intent. "
        "Determine if it contains phishing attempts, scamming language, hate speech, "
        "or any other harmful content. Provide a concise assessment and explain your reasoning. "
        "Output your response in a clear, easy-to-read format, starting with 'Assessment: ' (either 'Malicious' or 'Not Malicious'), then 'Reasoning: ', and finally 'ConfidenceScore: ' (a number from 1-100)."
    )
    result = await generate_gemini_content(prompt=prompt, image_data=image_data, text_input=text)
    return result

@app.post("/api/v1/check-scam")
async def check_scam(file: UploadFile = File(...)): 
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    image_data = await file.read()
    prompt = (
        "Analyze this image of a product or product listing. "
        "Based on visual cues, common sense, and general knowledge, "
        "determine if the product appears to be a scam or if it can genuinely do what it claims. "
        "Provide a concise assessment and explain your reasoning. "
        "Focus on whether the product's claims seem plausible or exaggerated/deceptive. "
        "Output your response in a clear, easy-to-read format, starting with 'Assessment: ' (either 'Scam' or 'Real'), then 'Reasoning: ', and finally 'ConfidenceScore: ' (a number from 1-100)."
    )
    result = await generate_gemini_content(prompt=prompt, image_data=image_data)
    return result

@app.post("/api/v1/verify-authenticity")
async def verify_authenticity(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    image_data = await file.read()
    prompt = (
        "Analyze this image of a product. "
        "Based on visual cues, branding, packaging, and general knowledge, "
        "determine if this product appears to be a genuine/official version or a fake/unofficial one. "
        "Provide a concise assessment and explain your reasoning. "
        "Focus on details that indicate authenticity or lack thereof, such as logos, quality, and design. "
        "Output your response in a clear, easy-to-read format, starting with 'Assessment: ' (either 'Fake' or 'Genuine'), then 'Reasoning: ', and finally 'ConfidenceScore: ' (a number from 1-100)."
    )
    result = await generate_gemini_content(prompt=prompt, image_data=image_data)
    return result

@app.post("/api/v1/check-url-malicious-intent")
async def check_url_malicious_intent(url: str = Form(...)): 
    try:

        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract all text from the body, excluding script and style tags
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        text_content = soup.get_text(separator=' ', strip=True)

        if not text_content:
            prompt_text = (
                f"Analyze the URL name '{url}' for malicious intent. Since no readable text was found on the page, "
                "base your assessment solely on the URL name (domain, path segments). "
                "Determine if it suggests phishing attempts, scamming, or other harmful content. "
                "Provide a concise assessment and explain your reasoning. "
                "Output your response in a clear, easy-to-read format, starting with 'Assessment: ' (either 'Malicious' or 'Not Malicious'), then 'Reasoning: ', and finally 'ConfidenceScore: ' (a number from 1-100)."
            )
            gemini_response = await generate_gemini_content(prompt=prompt_text, text_input=url)
        else:
            prompt_text = (
                f"Analyze the provided content scraped from the URL '{url}' for malicious intent. "
                "Determine if the website contains phishing attempts, scamming language, hate speech, "
                "or any other harmful content. "
                "Provide a concise assessment and explain your reasoning. "
                "Output your response in a clear, easy-to-read format, starting with 'Assessment: ' (either 'Malicious' or 'Not Malicious'), then 'Reasoning: ', and finally 'ConfidenceScore: ' (a number from 1-100)."
            )
            gemini_response = await generate_gemini_content(prompt=prompt_text, text_input=text_content)

        return gemini_response
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error accessing the URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the ScamOrNot API! Use /api/v1/check-scam or /api/v1/verify-authenticity endpoints."}