
# AI Web Content Summarizer

An AI-powered web application that summarizes webpage content using AWS Bedrock and SageMaker. Simply provide a URL, and the application will extract the content and generate a concise, understandable summary.

## Features

- 🤖 AI-powered summarization using AWS Bedrock (Claude 3 Haiku)
- 🌐 Web scraping with intelligent content extraction
- 📱 Clean, responsive web interface
- 🔄 Fallback summarization when Bedrock is unavailable
- ⚡ Fast and efficient processing
- 🛡️ Error handling and validation

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS credentials configured

## Installation

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## AWS Setup

### Option 1: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### Option 2: AWS CLI Configuration
```bash
aws configure
```

### Option 3: IAM Role (for EC2/SageMaker)
If running on AWS infrastructure, attach an IAM role with Bedrock permissions.

## Required AWS Permissions

Your AWS credentials need the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:53111
   ```

3. Enter a URL in the input field and click "Summarize"

## Sample URLs to Test

- Federal Reserve Research: https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm
- Wikipedia Articles: https://en.wikipedia.org/wiki/Artificial_intelligence
- News Articles: https://www.bbc.com/news

## Configuration

You can customize the application behavior using environment variables:

- `AWS_REGION`: AWS region for Bedrock (default: us-east-1)
- `BEDROCK_MODEL_ID`: Bedrock model to use (default: Claude 3 Haiku)
- `MAX_CONTENT_LENGTH`: Maximum content length to process (default: 8000)
- `MAX_SUMMARY_TOKENS`: Maximum tokens for summary (default: 1000)
- `FLASK_PORT`: Port to run the web server (default: 53111)

## API Endpoints

### GET /
Returns the web interface

### POST /summarize
Summarizes content from a URL
```json
{
    "url": "https://example.com"
}
```

Response:
```json
{
    "success": true,
    "title": "Page Title",
    "url": "https://example.com",
    "summary": "AI-generated summary..."
}
```

### GET /health
Health check endpoint
```json
{
    "status": "healthy",
    "bedrock_available": true
}
```

## Architecture

The application consists of:

1. **Web Scraper**: Extracts content from URLs using BeautifulSoup
2. **AI Summarizer**: Uses AWS Bedrock (Claude 3 Haiku) for summarization
3. **Web Interface**: Flask-based web application with a clean UI
4. **Fallback System**: Provides basic summarization when Bedrock is unavailable

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are properly configured
   - Check IAM permissions for Bedrock access

2. **Bedrock Model Not Available**
   - Verify the model is available in your AWS region
   - Check if you have access to the specific model

3. **Content Extraction Fails**
   - Some websites may block automated requests
   - Try different URLs or check if the site requires authentication

4. **Rate Limiting**
   - Bedrock has rate limits; implement delays if needed
   - Consider using different models for different use cases

## Cost Considerations

- Claude 3 Haiku is cost-effective for summarization tasks
- Monitor your AWS Bedrock usage through the AWS Console
- Consider implementing caching for frequently requested URLs

## Security Notes

- Never commit AWS credentials to version control
- Use IAM roles when possible instead of access keys
- Implement rate limiting for production deployments
- Validate and sanitize all user inputs

## License

This project is for educational and demonstration purposes.

