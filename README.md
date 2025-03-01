# 🛠️ Website Chatbot 🤖

A **serverless AI chatbot** that allows users to enter a **website URL** and ask **questions** about its content. The project utilizes **AWS Lambda, API Gateway, S3 (Static Website Hosting), LangChain, OpenAI (GPT-4o-mini), and BeautifulSoup** for web scraping.

## 🚀 Live Demo  
👉 [Website Chatbot](http://website-chatbot-ui.s3-website-ap-southeast-2.amazonaws.com/)  

---

## 📌 Features  

✅ **Enhanced Web Scraping**: Extracts comprehensive content including headings, paragraphs, lists, and tables  
✅ **Recursive Scraping**: Crawls linked pages within the same domain for more comprehensive information  
✅ **JavaScript Support**: Experimental support for JavaScript-rendered content  
✅ **AI-Powered Responses**: Uses `LangChain` and `OpenAI` GPT-4o-mini to answer user questions based on scraped content  
✅ **Serverless Deployment**: Deployed using **AWS Lambda** & exposed via **API Gateway**  
✅ **Static Web UI**: Hosted on **AWS S3** for a lightweight user interface  
✅ **Fast & Scalable**: No need for backend servers; AWS handles scaling  

---

## 🏷️ Architecture Overview  

```
[User] --> [AWS S3 (Static UI)] --> [AWS API Gateway] --> [AWS Lambda] --> [LangChain + OpenAI]  
                                                   ↳ [Enhanced BeautifulSoup Scraper]
```

- **Frontend**: Simple `HTML + JavaScript` frontend hosted on **S3**
- **API**: AWS **API Gateway** routes requests to **Lambda**
- **Backend Logic**:
  - **Scrapes** website content via `requests` + `BeautifulSoup` with enhanced extraction
  - **Recursively crawls** linked pages for comprehensive information
  - **Processes** user query using `LangChain` + `GPT-4o-mini`
  - **Returns** AI-generated response via API  

---

## 🛠️ Tech Stack  

| Technology | Usage |
|------------|-------|
| **LangChain** | Handles LLM interactions with OpenAI |
| **OpenAI API (GPT-4o-mini)** | Processes natural language queries |
| **BeautifulSoup** | Enhanced scraping of text content from websites |
| **AWS Lambda** | Serverless backend function |
| **AWS API Gateway** | Routes HTTP requests to Lambda |
| **AWS S3** | Hosts the static HTML frontend |
| **JavaScript (Fetch API)** | Connects frontend with the API |
| **Python (Requests, JSON, OS)** | Backend logic |

---

## 📂 Project Structure  

```
📁 aws_lambda_chatbot
👀 ├── 📝 lambda_function.py        # AWS Lambda function (backend) with enhanced scraping
👀 ├── 📝 index.html                # Frontend UI with advanced options (hosted on S3)
👀 ├── 📁 package/                   # Python dependencies (for AWS Lambda)
👀 ├── 📝 output.txt                 # Lambda logs (for debugging)
👀 ├── 📝 .gitignore                 # Ignore unnecessary files
👀 └── 📝 README.md                  # Project documentation
```

---

## ⚙️ Setup & Deployment  

### **1 Clone the Repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/website-chatbot.git
cd website-chatbot
```

### **2 AWS Configuration**
Ensure you have **AWS CLI** configured:
```bash
aws configure
```
- **Set AWS Region:** `ap-southeast-2`
- **Set IAM User Credentials** (with permissions for **Lambda, API Gateway, and S3**)

---

### **3 Deploy Backend (AWS Lambda)**
1. **Install Dependencies Locally**
```bash
mkdir package
pip install requests beautifulsoup4 langchain openai -t package/
```

2. **Zip the Function for AWS Lambda**
```bash
cd package
zip -r ../lambda_function.zip .
cd ..
zip -g lambda_function.zip lambda_function.py
```

3. **Deploy to AWS Lambda**
```bash
aws lambda update-function-code \
    --function-name WebsiteChatbot \
    --zip-file fileb://lambda_function.zip \
    --region ap-southeast-2
```

4. **Configure API Gateway Route**
```bash
aws apigatewayv2 create-route \
    --api-id YOUR_API_ID \
    --route-key "GET /chat" \
    --target integrations/YOUR_INTEGRATION_ID \
    --region ap-southeast-2
```

---

### **4 Deploy Frontend (AWS S3)**
1. **Create an S3 Bucket**
```bash
aws s3 mb s3://website-chatbot-ui --region ap-southeast-2
```
2. **Enable Static Website Hosting**
```bash
aws s3 website s3://website-chatbot-ui --index-document index.html
```
3. **Upload `index.html`**
```bash
aws s3 cp index.html s3://website-chatbot-ui/
```
4. **Make the File Public**
```bash
aws s3api put-object-acl --bucket website-chatbot-ui --key index.html --acl public-read
```

---

## 🌍 Usage  

### **Frontend**
1. Open **[Website Chatbot UI](https://website-chatbot-ui.s3-website-ap-southeast-2.amazonaws.com/)**
2. Enter a **Website URL**
3. Type a **Question** about the website content
4. (Optional) Configure **Advanced Options**:
   - **Recursive Depth**: Control how deep the crawler should go (1-3 levels)
   - **Max Pages**: Limit the number of pages to scrape (5-20)
   - **JavaScript Rendering**: Enable experimental support for JS-rendered content
5. Click **"Ask Chatbot"**
6. Get an AI-generated response!

---

### **Backend (API Testing via `curl`)**
```bash
curl "https://YOUR-API-ID.execute-api.ap-southeast-2.amazonaws.com/default/chat?url=https://example.com&question=What%20is%20this%20website%20about?&max_depth=2&max_pages=10&handle_js=false"
```

Expected Response:
```json
{
    "answer": "This website provides information about..."
}
```

---

## 🛡️ Troubleshooting  

| Issue | Solution |
|--------|---------|
| **CORS Error** | Ensure API Gateway has `Access-Control-Allow-Origin: *` in responses |
| **Lambda Import Errors** | Make sure all dependencies are included in `package/` before zipping |
| **Failed to Fetch API** | Check if API Gateway **Stage Name** is correctly set in `index.html` |
| **Slow Response Times** | Reduce `max_depth` and `max_pages` values for faster responses |
| **JavaScript Rendering Issues** | JavaScript rendering is experimental; try with `handle_js=false` |

---

##  License  

This project is open-source and available under the **MIT License**.

---

##  Contributions  

Contributions are **welcome**! If you'd like to enhance this project:
1. **Fork** this repo
2. **Create a branch** (`feature-xyz`)
3. **Commit your changes**
4. **Open a Pull Request**



