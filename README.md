# ScamOrNot API

This API allows you to analyze product images to determine if a product/listing is a scam or if a product is genuine/fake, leveraging Google's Gemini Pro Vision model.

## Features

*   **Scam Check**: Determine if a product can genuinely do what it claims.
*   **Authenticity Verification**: Verify if a product is a real/official version or a fake/unofficial one.

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
*   **Response**: `application/json` with `{"Assessment": "...", "Reasoning": "...", "ConfidenceScore": ...}`

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
*   **Response**: `application/json` with `{"Assessment": "...", "Reasoning": "...", "ConfidenceScore": ...}`

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

### 4. URL Malicious Intent Check

Scrapes text from a given URL and assesses its malicious intent.

*   **Endpoint**: `/api/v1/check-url-malicious-intent`
*   **Method**: `POST`
*   **Content-Type**: `application/json`
*   **JSON Body**: 
    *   `url` (required): The URL to scrape and analyze.
*   **Response**: `application/json` with `{"Assessment": "...", "Reasoning": "...", "ConfidenceScore": ...}`

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/check-url-malicious-intent" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://example.com/suspicious-page"}'
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