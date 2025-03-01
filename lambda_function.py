import json
import requests
import re
import time
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
import os
from urllib.parse import urljoin, urlparse
import concurrent.futures

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def is_same_domain(url, base_url):
    """Check if the URL is from the same domain as the base URL."""
    return urlparse(url).netloc == urlparse(base_url).netloc

def extract_content(soup):
    """Extract relevant content from the soup object."""
    # Extract headings
    headings = []
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for heading in soup.find_all(tag):
            headings.append(f"{tag.upper()}: {heading.get_text().strip()}")
    
    # Extract paragraphs
    paragraphs = [para.get_text().strip() for para in soup.find_all('p')]
    
    # Extract list items
    list_items = [f"• {item.get_text().strip()}" for item in soup.find_all('li')]
    
    # Extract table data
    table_data = []
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                table_data.append(" | ".join([cell.get_text().strip() for cell in cells]))
    
    # Combine all content
    all_content = headings + paragraphs + list_items + table_data
    
    # Filter out empty strings and join with newlines
    return "\n".join([content for content in all_content if content.strip()])

def scrape_website(url, max_depth=1, max_pages=5, handle_js=False):
    """
    Extract text content from a given website with enhanced features.
    
    Args:
        url (str): The URL to scrape
        max_depth (int): Maximum depth for recursive scraping
        max_pages (int): Maximum number of pages to scrape
        handle_js (bool): Whether to handle JavaScript-rendered content
        
    Returns:
        str: Extracted content
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    # For JavaScript rendering, we would use a headless browser
    # Since AWS Lambda has limitations with browser automation,
    # we'll implement a simplified version that can be expanded later
    if handle_js:
        try:
            # This is a placeholder for JavaScript rendering
            # In a real implementation, you would use a service like AWS Lambda Layers
            # to include Selenium/Playwright or use a separate service like Browserless
            return "JavaScript rendering is not supported in this version. Please upgrade to enable this feature."
        except Exception as e:
            return f"Error with JavaScript rendering: {str(e)}"
    
    # For regular scraping
    try:
        # Set for visited URLs to avoid duplicates
        visited_urls = set()
        all_content = []
        urls_to_visit = [(url, 0)]  # (url, depth)
        
        while urls_to_visit and len(visited_urls) < max_pages:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            content = extract_content(soup)
            
            if content:
                all_content.append(f"--- Content from {current_url} ---")
                all_content.append(content)
            
            # If we haven't reached max depth, add links to queue
            if depth < max_depth:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # Skip fragment links and non-HTTP links
                    if href.startswith('#') or not (href.startswith('http') or href.startswith('/')):
                        continue
                    
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)
                    
                    # Only process links from the same domain
                    if is_same_domain(absolute_url, url) and absolute_url not in visited_urls:
                        urls_to_visit.append((absolute_url, depth + 1))
        
        combined_content = "\n\n".join(all_content)
        return combined_content if combined_content else "No readable text found on this website."
    
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
    
    # Get optional parameters with defaults
    max_depth = int(params.get("max_depth", 1))
    max_pages = int(params.get("max_pages", 5))
    handle_js = params.get("handle_js", "false").lower() == "true"

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

    # Scrape website content with enhanced options
    website_content = scrape_website(website_url, max_depth, max_pages, handle_js)
    
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
