import json
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
import os

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def scrape_website(url):
    """Extract text content from a given website."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join([para.get_text() for para in paragraphs])
        return text if text else "No readable text found on this website."
    except requests.exceptions.RequestException as e:
        return f"Error fetching the website: {str(e)}"

def lambda_handler(event, context):
    """Lambda function to process the request and return chatbot response."""
    # Ensure API key is available
    if not OPENAI_API_KEY:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"error": "Missing OpenAI API Key"})
        }

    # Extract query parameters
    params = event.get("queryStringParameters", {})
    website_url = params.get("url") if params else None
    question = params.get("question") if params else None

    if not website_url or not question:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"error": "Missing parameters: 'url' and 'question' are required"})
        }

    # Scrape website content
    website_content = scrape_website(website_url)
    
    # Initialize ChatGPT
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
    prompt = f"Here is the content of the website:\n\n{website_content}\n\nNow answer this question: {question}"

    try:
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else response
    except Exception as e:
        answer = f"Error processing request: {str(e)}"

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Allows requests from any origin
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps({"answer": answer})
    }
