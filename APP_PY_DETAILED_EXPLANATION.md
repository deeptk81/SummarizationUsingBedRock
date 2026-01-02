
# 📄 Complete Explanation of `app.py`

## 🎯 Overview
`app.py` is the core Flask application that powers your AI Web Content Summarizer. It integrates AWS Bedrock for AI summarization, web scraping capabilities, and serves both a simple HTML interface and a modern Angular frontend.

---

## 📚 Imports and Dependencies

```python
import boto3                    # AWS SDK for Bedrock integration
import requests                 # HTTP requests for web scraping
from bs4 import BeautifulSoup  # HTML parsing and content extraction
from flask import Flask, request, jsonify, render_template_string, send_from_directory, send_file
import json                     # JSON handling for API responses
import re                       # Regular expressions for text processing
from urllib.parse import urlparse  # URL validation and parsing
import logging                  # Application logging
```

### **Purpose of Each Import:**
- **`boto3`**: Connects to AWS Bedrock for AI summarization
- **`requests`**: Fetches webpage content from URLs
- **`BeautifulSoup`**: Parses HTML and extracts meaningful text
- **`Flask`**: Web framework for API endpoints and serving interfaces
- **`json`**: Handles JSON data for API communication
- **`re`**: Cleans and processes extracted text
- **`urlparse`**: Validates URL format before processing
- **`logging`**: Tracks application behavior and errors

---

## 🔧 Configuration and Setup

```python
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
```

### **What This Does:**
- **Logging Setup**: Configures INFO-level logging to track application behavior
- **Flask App**: Creates the main Flask application instance

---

## 🏗️ WebContentSummarizer Class

This is the heart of the application - a comprehensive class that handles all content processing and AI summarization.

### **1. Initialization (`__init__`)**

```python
def __init__(self):
    # Initialize AWS Bedrock client
    try:
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1'  # You can change this to your preferred region
        )
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {e}")
        self.bedrock_client = None
```

#### **What This Does:**
- **AWS Connection**: Attempts to connect to AWS Bedrock in the `us-east-1` region
- **Error Handling**: If AWS credentials aren't configured, it gracefully fails and sets `bedrock_client` to `None`
- **Fallback Ready**: The application can still work without Bedrock using fallback summarization

#### **AWS Requirements:**
- AWS credentials must be configured (IAM role, environment variables, or AWS CLI)
- Bedrock service must be available in the specified region
- Proper permissions for `bedrock-runtime` service

### **2. Content Extraction (`extract_content_from_url`)**

```python
def extract_content_from_url(self, url):
    """Extract text content from a webpage"""
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
```

#### **Browser Simulation:**
- **User-Agent Header**: Mimics a real Chrome browser to avoid bot detection
- **Timeout**: 30-second limit prevents hanging on slow websites
- **Error Handling**: `raise_for_status()` throws exceptions for HTTP errors (404, 500, etc.)

```python
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
```

#### **HTML Cleaning:**
- **BeautifulSoup Parser**: Converts HTML into a navigable tree structure
- **Element Removal**: Removes non-content elements:
  - `script`: JavaScript code
  - `style`: CSS styling
  - `nav`: Navigation menus
  - `header`: Page headers
  - `footer`: Page footers
- **`decompose()`**: Completely removes elements from memory

```python
        # Extract text from common content areas
        content_selectors = [
            'article', 'main', '.content', '#content', 
            '.post-content', '.entry-content', '.article-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text() for elem in elements])
                break
        
        # If no specific content area found, get all text
        if not content:
            content = soup.get_text()
```

#### **Smart Content Detection:**
- **Priority Selectors**: Looks for common content containers first
- **Semantic HTML**: Targets `<article>` and `<main>` tags
- **Common Classes**: Searches for typical content class names
- **Fallback Strategy**: If no specific content area found, extracts all text
- **Text Extraction**: `get_text()` converts HTML elements to plain text

```python
        # Clean up the text
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Get page title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        return {
            'title': title_text,
            'content': content,
            'url': url
        }
```

#### **Text Processing:**
- **Whitespace Normalization**: `re.sub(r'\s+', ' ', content)` replaces multiple spaces/newlines with single spaces
- **Title Extraction**: Gets the page title from `<title>` tag
- **Structured Return**: Returns a dictionary with title, content, and URL

### **3. AI Summarization (`summarize_with_bedrock`)**

```python
def summarize_with_bedrock(self, content, title=""):
    """Summarize content using AWS Bedrock"""
    if not self.bedrock_client:
        return "AWS Bedrock client not available. Please configure AWS credentials."
    
    try:
        # Truncate content if too long (Bedrock has token limits)
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
```

#### **Content Preparation:**
- **Client Check**: Verifies Bedrock client is available
- **Token Limit**: Truncates content to 8000 characters to stay within model limits
- **Graceful Truncation**: Adds "..." to indicate content was cut off

```python
        # Create prompt for summarization
        prompt = f"""
        Please provide a concise and understandable summary of the following webpage content.
        
        Title: {title}
        
        Content: {content}
        
        Summary requirements:
        - Keep it concise but comprehensive
        - Focus on key points and main ideas
        - Make it understandable for a general audience
        - Structure it with clear paragraphs if needed
        - Limit to 3-4 paragraphs maximum
        
        Summary:
        """
```

#### **Prompt Engineering:**
- **Clear Instructions**: Tells the AI exactly what kind of summary to create
- **Context Inclusion**: Provides both title and content for better understanding
- **Quality Guidelines**: Specifies conciseness, comprehensiveness, and readability
- **Structure Requirements**: Requests clear paragraphs and length limits
- **Audience Consideration**: Asks for general audience accessibility

```python
        # Use Claude 3 Haiku for cost-effective summarization
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        summary = response_body['content'][0]['text']
        
        return summary
```

#### **Bedrock API Integration:**
- **Model Selection**: Uses Claude 3 Haiku (cost-effective, fast, good quality)
- **API Version**: Specifies Anthropic's Bedrock API version
- **Token Limit**: Sets maximum response length to 1000 tokens
- **Message Format**: Uses Anthropic's chat message format
- **Response Processing**: Extracts the summary text from the API response

### **4. Fallback Summarization (`fallback_summarize`)**

```python
def fallback_summarize(self, content, title=""):
    """Fallback summarization method when Bedrock is not available"""
    # Simple extractive summarization
    sentences = content.split('.')
    # Take first few sentences and some key sentences
    summary_sentences = sentences[:3]
    
    # Look for sentences with key terms
    key_terms = ['conclusion', 'result', 'finding', 'important', 'significant', 'main']
    for sentence in sentences[3:]:
        if any(term in sentence.lower() for term in key_terms):
            summary_sentences.append(sentence)
            if len(summary_sentences) >= 6:
                break
    
    summary = '. '.join(summary_sentences).strip()
    if summary and not summary.endswith('.'):
        summary += '.'
        
    return f"**Fallback Summary** (Bedrock not available):\n\n{summary}"
```

#### **Extractive Summarization Logic:**
- **Sentence Splitting**: Breaks content into sentences using periods
- **Lead Sentences**: Takes first 3 sentences (often contain key information)
- **Keyword Detection**: Looks for sentences containing important terms
- **Smart Selection**: Finds sentences with conclusion-related keywords
- **Length Control**: Limits to maximum 6 sentences
- **Formatting**: Ensures proper punctuation and clear labeling

---

## 🌐 Flask Routes and Web Interface

### **1. HTML Template (`HTML_TEMPLATE`)**

The application includes a complete HTML interface embedded as a string:

```python
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Web Content Summarizer</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        input[type="url"] { width: 70%; padding: 10px; margin: 10px 0; }
        button { padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a87; }
        .summary { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007cba; }
        .error { background: #ffe6e6; border-left: 4px solid #ff0000; }
        .loading { color: #666; font-style: italic; }
        .title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }
        .url { color: #666; font-size: 0.9em; margin-bottom: 15px; word-break: break-all; }
    </style>
</head>
```

#### **CSS Features:**
- **Responsive Design**: Max-width container centers content
- **Professional Styling**: Clean, modern appearance
- **Visual Feedback**: Different styles for loading, success, and error states
- **Accessibility**: Good contrast ratios and readable fonts
- **Interactive Elements**: Hover effects on buttons

```html
<body>
    <h1>🤖 AI Web Content Summarizer</h1>
    <p>Enter a URL to get an AI-powered summary of the webpage content using AWS Bedrock.</p>
    
    <div class="container">
        <form id="summaryForm">
            <input type="url" id="urlInput" placeholder="https://example.com" required>
            <button type="submit">Summarize</button>
        </form>
    </div>
    
    <div id="result"></div>
    
    <div class="container">
        <h3>Sample URLs to try:</h3>
        <ul>
            <li><a href="#" onclick="document.getElementById('urlInput').value='https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm'">Federal Reserve Research Paper</a></li>
            <li><a href="#" onclick="document.getElementById('urlInput').value='https://en.wikipedia.org/wiki/Artificial_intelligence'">Wikipedia - AI</a></li>
            <li><a href="#" onclick="document.getElementById('urlInput').value='https://www.bbc.com/news'">BBC News</a></li>
        </ul>
    </div>
```

#### **HTML Structure:**
- **Form Validation**: Uses `type="url"` and `required` for client-side validation
- **Sample URLs**: Provides ready-to-test examples
- **Result Container**: Dynamic area for displaying summaries
- **User Experience**: Clear instructions and helpful examples

```javascript
<script>
    document.getElementById('summaryForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('urlInput').value;
        const resultDiv = document.getElementById('result');
        
        resultDiv.innerHTML = '<div class="summary loading">🔄 Processing URL and generating summary...</div>';
        
        try {
            const response = await fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            });
            
            const data = await response.json();
            
            if (data.success) {
                resultDiv.innerHTML = `
                    <div class="summary">
                        <div class="title">${data.title}</div>
                        <div class="url">Source: ${data.url}</div>
                        <div>${data.summary.split('\\n').join('<br>')}</div>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div class="summary error">❌ Error: ${data.error}</div>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="summary error">❌ Network error: ${error.message}</div>`;
        }
    });
</script>
```

#### **JavaScript Features:**
- **Modern Async/Await**: Uses modern JavaScript for API calls
- **Form Prevention**: Prevents default form submission
- **Loading States**: Shows processing indicator during API calls
- **Error Handling**: Catches and displays both API and network errors
- **Dynamic Content**: Updates page content without refresh
- **Text Formatting**: Converts newlines to HTML line breaks

### **2. Flask Route Handlers**

#### **Home Route (`/`)**
```python
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
```
- **Simple Interface**: Serves the HTML template for basic usage
- **Template Rendering**: Uses Flask's `render_template_string` to serve embedded HTML

#### **Summarization API (`/summarize`)**
```python
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'success': False, 'error': 'Invalid URL format'})
```

#### **Input Validation:**
- **JSON Parsing**: Extracts URL from POST request body
- **Required Field Check**: Ensures URL is provided
- **URL Format Validation**: Uses `urlparse` to verify URL structure
- **Scheme Check**: Ensures URL has http:// or https://
- **Domain Check**: Ensures URL has a valid domain name

```python
        # Extract content from URL
        logger.info(f"Extracting content from: {url}")
        content_data = summarizer.extract_content_from_url(url)
        
        if not content_data:
            return jsonify({'success': False, 'error': 'Failed to extract content from URL'})
        
        # Generate summary
        logger.info("Generating summary...")
        if summarizer.bedrock_client:
            summary = summarizer.summarize_with_bedrock(
                content_data['content'], 
                content_data['title']
            )
        else:
            summary = summarizer.fallback_summarize(
                content_data['content'], 
                content_data['title']
            )
        
        return jsonify({
            'success': True,
            'title': content_data['title'],
            'url': url,
            'summary': summary
        })
```

#### **Processing Logic:**
- **Content Extraction**: Calls the web scraping method
- **Error Handling**: Returns error if content extraction fails
- **AI vs Fallback**: Chooses summarization method based on Bedrock availability
- **Structured Response**: Returns JSON with success status and data
- **Logging**: Tracks processing steps for debugging

#### **Health Check (`/health`)**
```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'bedrock_available': summarizer.bedrock_client is not None})
```
- **Service Status**: Indicates if the application is running
- **Bedrock Status**: Shows whether AI summarization is available
- **Monitoring**: Useful for deployment health checks

### **3. Angular Frontend Integration**

```python
# Angular Frontend Routes
import os

# Path to Angular build files
ANGULAR_DIST_PATH = os.path.join(os.path.dirname(__file__), 'angular-summarizer', 'dist')

@app.route('/app')
@app.route('/app/')
@app.route('/app/<path:path>')
def serve_angular_app(path=''):
    """Serve the Angular application"""
    try:
        if path and os.path.exists(os.path.join(ANGULAR_DIST_PATH, path)):
            return send_from_directory(ANGULAR_DIST_PATH, path)
        else:
            return send_from_directory(ANGULAR_DIST_PATH, 'index.html')
    except Exception as e:
        logger.error(f"Error serving Angular app: {e}")
        return f"Angular app not found. Please build the Angular application first.", 404
```

#### **Angular Serving Logic:**
- **Path Resolution**: Finds Angular build files relative to app.py
- **Route Handling**: Serves different Angular routes
- **File Serving**: Returns specific files if they exist
- **SPA Support**: Falls back to index.html for Angular routing
- **Error Handling**: Provides helpful error message if Angular app not built

```python
@app.route('/assets/<path:filename>')
def serve_angular_assets(filename):
    """Serve Angular static assets"""
    try:
        return send_from_directory(os.path.join(ANGULAR_DIST_PATH, 'assets'), filename)
    except Exception as e:
        logger.error(f"Error serving Angular assets: {e}")
        return "Asset not found", 404
```

#### **Asset Serving:**
- **Static Files**: Serves CSS, JavaScript, images, and other assets
- **Path Security**: Uses Flask's `send_from_directory` for safe file serving
- **Error Handling**: Returns 404 for missing assets

---

## 🚀 Application Startup

```python
if __name__ == '__main__':
    print("🚀 Starting AI Web Content Summarizer...")
    print("📝 This application uses AWS Bedrock for AI-powered summarization")
    print("🌐 Access the web interfaces at:")
    print("   • Simple HTML Interface: http://localhost:57969")
    print("   • Modern Angular App: http://localhost:57969/app")
    print("   • API Health Check: http://localhost:57969/health")
    print("\n⚠️  Note: Make sure your AWS credentials are configured for Bedrock access")
    
    app.run(host='0.0.0.0', port=57969, debug=False)
```

#### **Startup Configuration:**
- **Host Binding**: `0.0.0.0` allows access from any IP address
- **Port**: Uses port 57969 (configurable)
- **Debug Mode**: Disabled for production use
- **User Guidance**: Provides clear instructions on how to access the application
- **AWS Reminder**: Warns about credential requirements

---

## 🔄 Application Flow

### **Complete Request Flow:**

1. **User Input**: User enters URL in either HTML or Angular interface
2. **URL Validation**: Application validates URL format
3. **Content Extraction**: 
   - Fetches webpage with browser headers
   - Parses HTML with BeautifulSoup
   - Removes non-content elements
   - Extracts main content using smart selectors
   - Cleans and normalizes text
4. **AI Summarization**:
   - If Bedrock available: Uses Claude 3 Haiku for AI summary
   - If Bedrock unavailable: Uses extractive fallback method
5. **Response**: Returns structured JSON with title, URL, and summary
6. **Display**: Interface shows formatted summary to user

### **Error Handling at Each Step:**

- **Network Errors**: Timeout, connection failures, HTTP errors
- **Content Errors**: Empty content, parsing failures
- **AI Errors**: Bedrock unavailable, API failures, token limits
- **Validation Errors**: Invalid URLs, missing parameters

### **Fallback Mechanisms:**

- **No Bedrock**: Uses extractive summarization
- **Content Extraction Failure**: Returns helpful error message
- **Network Issues**: Provides clear error feedback

---

## 🎯 Key Features Summary

### **1. Robust Web Scraping:**
- Browser simulation to avoid bot detection
- Smart content extraction with multiple strategies
- Comprehensive HTML cleaning and text processing

### **2. AI Integration:**
- AWS Bedrock with Claude 3 Haiku model
- Intelligent prompt engineering for quality summaries
- Graceful fallback when AI unavailable

### **3. Dual Interface:**
- Simple HTML interface for quick testing
- Modern Angular SPA for enhanced user experience
- RESTful API for programmatic access

### **4. Production Ready:**
- Comprehensive error handling and logging
- Health monitoring endpoints
- Secure file serving for Angular assets
- Configurable deployment options

### **5. User Experience:**
- Loading states and progress indicators
- Clear error messages and guidance
- Sample URLs for easy testing
- Responsive design for mobile devices

This `app.py` file represents a complete, production-ready web application that successfully combines modern web technologies, AI capabilities, and robust engineering practices! 🎉

