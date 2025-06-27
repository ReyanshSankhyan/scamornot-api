# ScamOrNot API

This API allows you to analyze product images to determine if a product/listing is a scam or if a product is genuine/fake, leveraging Google's Gemini Pro Vision model.

## Features

*   **Scam Check**: Determine if a product can genuinely do what it claims.
*   **Authenticity Verification**: Verify if a product is a real/official version or a fake/unofficial one.
*   **URL Malicious Intent Check**: Analyze a given URL for phishing attempts, scamming language, hate speech, or other harmful content.

## Usage

### Check Malicious Text/Image

To check text or an image for malicious intent, send a `POST` request to `/api/v1/check-malicious-text`.

**Request Body Options:**

*   **Text only:**

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"text": "Your text to analyze"}' http://localhost:8000/api/v1/check-malicious-text
    ```

*   **Image only:**

    ```bash
    curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/api/v1/check-malicious-text
    ```

*   **Text and Image:**

    ```bash
    curl -X POST -F "text=Your text to analyze" -F "file=@/path/to/your/image.jpg" http://localhost:8000/api/v1/check-malicious-text
    ```

**Response Format:**

```json
{
  "Assessment": "Malicious" || "Not Malicious",
  "Reasoning": "Explanation of the assessment.",
  "ConfidenceScore": 1-100
}
```

### Check Scam (Image)

To check if a product image appears to be a scam, send a `POST` request to `/api/v1/check-scam` with the image file.

```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/api/v1/check-scam
```

**Response Format:**

```json
{
  "Assessment": "Scam" || "Real",
  "Reasoning": "Explanation of the assessment.",
  "ConfidenceScore": 1-100
}
```

### Verify Authenticity (Image)

To verify the authenticity of a product image, send a `POST` request to `/api/v1/verify-authenticity` with the image file.

```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/api/v1/verify-authenticity
```

**Response Format:**

```json
{
  "Assessment": "Fake" || "Genuine",
  "Reasoning": "Explanation of the assessment.",
  "ConfidenceScore": 1-100
}
```

### Check URL Malicious Intent

To check a URL for malicious intent, send a `POST` request to `/api/v1/check-url-malicious-intent` with the URL as a form parameter.

```bash
curl -X POST -F "url=https://example.com" http://localhost:8000/api/v1/check-url-malicious-intent
```

**Response Format:**

```json
{
  "Assessment": "Malicious" || "Not Malicious",
  "Reasoning": "Explanation of why the URL is considered malicious or not.",
  "ConfidenceScore": 1-100
}
```

## Setup

1.  **Clone the repository (if applicable) or navigate to the project directory:**

    ```bash
    cd /Users/69249/Documents/Coding/scamornot
    ```

2.  **Create a Python Virtual Environment (recommended):**

    ```bash
    python3 -m venv venv
    ```

3.  **Activate the Virtual Environment:**

    *   On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

    *   On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up your Gemini API Key:**

    *   Obtain a Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Open the `.env` file in the project root.
    *   Replace `your_api_key_here` with your actual Gemini API key:

        ```
        GEMINI_API_KEY=your_api_key_here
        ```

## Running the API

To run the API locally, use Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

### 1. Scam Check

Determines if a product appears to be a scam or can genuinely do what it claims.

*   **Endpoint**: `/api/v1/check-scam`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data`
*   **Form Field**: `file` (your image file)
*   **Response**: `application/json` with `{"Assessment": "...", "Reasoning": "..."}`

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/check-scam" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg;type=image/jpeg"
```

### 2. Authenticity Verification

Verifies if a product is a genuine/official version or a fake/unofficial one.

*   **Endpoint**: `/api/v1/verify-authenticity`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data`
*   **Form Field**: `file` (your image file)
*   **Response**: `application/json` with `{"MaliciousScore": ..., "Reasoning": "..."}`

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/verify-authenticity" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg;type=image/jpeg"
```

### 3. Malicious Text Check

Determines if a given text or text within an image has malicious intent.

*   **Endpoint**: `/api/v1/check-malicious-text`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data` or `application/json`
*   **Form Fields/JSON Body**: 
    *   `text` (optional): A string of text to analyze.
    *   `file` (optional): An image file containing text to analyze.
*   **Response**: `application/json` with `{"MaliciousScore": ..., "Reasoning": "..."}`

**Example using `curl` with text input:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/check-malicious-text" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a suspicious message."}'
```

**Example using `curl` with image input:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/check-malicious-text" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image_with_text.png;type=image/png"
```

The `/api/v1/check-url-malicious-intent` endpoint allows you to check the malicious intent of content found at a given URL. It scrapes text from the URL and uses the Gemini model for analysis. If no readable text is found on the page, the AI will assess based solely on the URL name.

- **Method**: `POST`
- **URL**: `/api/v1/check-url-malicious-intent`
- **Request Body**: `{"url": "<your_url_here>"}`
- **Response**: `{"MaliciousScore": <score>, "Reasoning": "<reasoning_text>"}`

  The parsing logic for the AI's response has been improved to ensure accurate extraction of both the `MaliciousScore` and `Reasoning`.

  **Example `curl` command**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/check-url-malicious-intent" \
       -H "Content-Type: application/json" \
       -d '{"url": "https://www.example.com"}'
  ```

### Root Endpoint

*   **Endpoint**: `/`
*   **Method**: `GET`

Returns a welcome message.

## Deployment Guide

For deployment, consider these options:

*   **Serverless Platforms**: AWS Lambda, Google Cloud Functions, Azure Functions. These are cost-effective for APIs with fluctuating traffic and handle scaling automatically.
*   **Containerization**: Dockerize your application and deploy it to platforms like Google Cloud Run, AWS ECS/EKS, or Kubernetes. This provides more control and portability.

**General Steps for Deployment (e.g., to Google Cloud Run):**

1.  **Containerize your application**: Create a `Dockerfile`.
2.  **Build and push the Docker image**: To a container registry (e.g., Google Container Registry, Docker Hub).
3.  **Deploy to Cloud Run**: Specify the image, environment variables (for `GEMINI_API_KEY`), and other settings.

*(A detailed `Dockerfile` and deployment instructions can be provided upon request.)*