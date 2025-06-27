import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Optional
import io
from PIL import Image

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
async def generate_gemini_content(image_data: bytes, prompt: str):
    try:
        # Open the image using Pillow
        img = Image.open(io.BytesIO(image_data))
        model = genai.GenerativeModel('gemini-1.5-flash') # Updated model name
        response = model.generate_content([prompt, img])
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
    result = await generate_gemini_content(image_data, prompt)
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
    result = await generate_gemini_content(image_data, prompt)
    return result

@app.get("/")
async def read_root():
    return {"message": "Welcome to the ScamOrNot API! Use /api/v1/check-scam or /api/v1/verify-authenticity endpoints."}