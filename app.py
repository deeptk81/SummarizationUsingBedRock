import boto3
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string, send_from_directory, send_file
import json
import re
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebContentSummarizer:
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
    
    def extract_content_from_url(self, url):
        """Extract text content from a webpage"""
        try:
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
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
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def summarize_with_bedrock(self, content, title=""):
        """Summarize content using AWS Bedrock"""
        if not self.bedrock_client:
            return "AWS Bedrock client not available. Please configure AWS credentials."
        
        try:
            # Truncate content if too long (Bedrock has token limits)
            max_content_length = 8000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
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
            
        except Exception as e:
            logger.error(f"Error with Bedrock summarization: {e}")
            return f"Error generating summary: {str(e)}"
    
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

# Initialize the summarizer
summarizer = WebContentSummarizer()

# HTML template for the web interface
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
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
        
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'bedrock_available': summarizer.bedrock_client is not None})

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

@app.route('/assets/<path:filename>')
def serve_angular_assets(filename):
    """Serve Angular static assets"""
    try:
        return send_from_directory(os.path.join(ANGULAR_DIST_PATH, 'assets'), filename)
    except Exception as e:
        logger.error(f"Error serving Angular assets: {e}")
        return "Asset not found", 404

if __name__ == '__main__':
    print("🚀 Starting AI Web Content Summarizer...")
    print("📝 This application uses AWS Bedrock for AI-powered summarization")
    print("🌐 Access the web interfaces at:")
    print("   • Simple HTML Interface: http://localhost:57969")
    print("   • Modern Angular App: http://localhost:57969/app")
    print("   • API Health Check: http://localhost:57969/health")
    print("\n⚠️  Note: Make sure your AWS credentials are configured for Bedrock access")
    
    app.run(host='0.0.0.0', port=57969, debug=False)
