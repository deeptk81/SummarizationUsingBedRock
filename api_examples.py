
#!/usr/bin/env python3

"""
AI Web Content Summarizer - API Usage Examples
This file demonstrates various ways to invoke the API
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:57969"
HEADERS = {"Content-Type": "application/json"}

def example_1_basic_usage():
    """Basic API usage example"""
    print("📝 Example 1: Basic API Usage")
    print("-" * 40)
    
    url_to_summarize = "https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm"
    
    payload = {"url": url_to_summarize}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/summarize",
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Success!")
                print(f"📄 Title: {data['title']}")
                print(f"🔗 URL: {data['url']}")
                print(f"📝 Summary:\n{data['summary']}")
            else:
                print(f"❌ API Error: {data['error']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Request failed: {e}")

def example_2_with_error_handling():
    """API usage with comprehensive error handling"""
    print("\n📝 Example 2: With Error Handling")
    print("-" * 40)
    
    def summarize_url(url: str) -> Dict[str, Any]:
        """Summarize a URL with proper error handling"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/summarize",
                headers=HEADERS,
                json={"url": url},
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            if data['success']:
                return {
                    'status': 'success',
                    'title': data['title'],
                    'summary': data['summary'],
                    'url': data['url']
                }
            else:
                return {
                    'status': 'error',
                    'error': data['error']
                }
                
        except requests.exceptions.Timeout:
            return {'status': 'error', 'error': 'Request timed out'}
        except requests.exceptions.ConnectionError:
            return {'status': 'error', 'error': 'Could not connect to API server'}
        except requests.exceptions.HTTPError as e:
            return {'status': 'error', 'error': f'HTTP error: {e}'}
        except Exception as e:
            return {'status': 'error', 'error': f'Unexpected error: {e}'}
    
    # Test with a valid URL
    result = summarize_url("https://en.wikipedia.org/wiki/Machine_learning")
    
    if result['status'] == 'success':
        print(f"✅ Successfully summarized: {result['title']}")
        print(f"📝 Summary: {result['summary'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")

def example_3_batch_processing():
    """Process multiple URLs in batch"""
    print("\n📝 Example 3: Batch Processing")
    print("-" * 40)
    
    urls_to_process = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm"
    ]
    
    results = []
    
    for i, url in enumerate(urls_to_process, 1):
        print(f"Processing {i}/{len(urls_to_process)}: {url[:50]}...")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/summarize",
                headers=HEADERS,
                json={"url": url},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    results.append({
                        'url': url,
                        'title': data['title'],
                        'summary': data['summary'],
                        'status': 'success'
                    })
                    print(f"  ✅ Success: {data['title'][:50]}...")
                else:
                    results.append({
                        'url': url,
                        'error': data['error'],
                        'status': 'error'
                    })
                    print(f"  ❌ Error: {data['error']}")
            else:
                results.append({
                    'url': url,
                    'error': f'HTTP {response.status_code}',
                    'status': 'error'
                })
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e),
                'status': 'error'
            })
            print(f"  💥 Exception: {e}")
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n📊 Batch Results: {successful}/{len(urls_to_process)} successful")
    
    return results

async def example_4_async_usage():
    """Asynchronous API usage for better performance"""
    print("\n📝 Example 4: Async Usage")
    print("-" * 40)
    
    async def summarize_async(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Async function to summarize a URL"""
        try:
            async with session.post(
                f"{API_BASE_URL}/summarize",
                headers=HEADERS,
                json={"url": url},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                data = await response.json()
                
                if response.status == 200 and data['success']:
                    return {
                        'url': url,
                        'title': data['title'],
                        'summary': data['summary'],
                        'status': 'success'
                    }
                else:
                    return {
                        'url': url,
                        'error': data.get('error', f'HTTP {response.status}'),
                        'status': 'error'
                    }
                    
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
    
    urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Flask_(web_framework)"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [summarize_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['title'][:50]}...")
        else:
            print(f"❌ Error for {result['url'][:50]}...: {result['error']}")

def example_5_health_check():
    """Check API health before making requests"""
    print("\n📝 Example 5: Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server Status: {health_data['status']}")
            print(f"🤖 Bedrock Available: {health_data['bedrock_available']}")
            
            if health_data['status'] == 'healthy':
                print("🚀 API is ready to use!")
                return True
            else:
                print("⚠️  API may not be fully functional")
                return False
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Health check error: {e}")
        return False

def example_6_curl_commands():
    """Show equivalent curl commands"""
    print("\n📝 Example 6: Equivalent cURL Commands")
    print("-" * 40)
    
    print("Health Check:")
    print("curl http://localhost:57969/health")
    
    print("\nSummarize URL:")
    print("""curl -X POST http://localhost:57969/summarize \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'""")
    
    print("\nWith timeout and formatted output:")
    print("""curl -X POST http://localhost:57969/summarize \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}' \\
  --max-time 60 | python -m json.tool""")

class APIClient:
    """Example 7: Object-oriented API client"""
    
    def __init__(self, base_url: str = "http://localhost:57969"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def summarize(self, url: str, timeout: int = 60) -> Dict[str, Any]:
        """Summarize a URL"""
        try:
            response = self.session.post(
                f"{self.base_url}/summarize",
                json={"url": url},
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the session"""
        self.session.close()

def example_7_oop_client():
    """Object-oriented API client usage"""
    print("\n📝 Example 7: OOP API Client")
    print("-" * 40)
    
    client = APIClient()
    
    try:
        # Health check
        health = client.health_check()
        print(f"Health: {health}")
        
        # Summarize
        if health.get('status') == 'healthy':
            result = client.summarize("https://en.wikipedia.org/wiki/REST")
            
            if result.get('success'):
                print(f"✅ Title: {result['title']}")
                print(f"📝 Summary: {result['summary'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error')}")
        
    finally:
        client.close()

def main():
    """Run all examples"""
    print("🤖 AI Web Content Summarizer - API Examples")
    print("=" * 60)
    
    # Check if API is available first
    if not example_5_health_check():
        print("\n⚠️  API is not available. Please start the server first:")
        print("   python app.py")
        return
    
    # Run examples
    example_1_basic_usage()
    example_2_with_error_handling()
    example_3_batch_processing()
    
    # Async example (commented out as it requires running event loop)
    # asyncio.run(example_4_async_usage())
    
    example_6_curl_commands()
    example_7_oop_client()
    
    print("\n🎉 All examples completed!")
    print("\n📚 Additional Resources:")
    print("- API Documentation: README.md")
    print("- Web Interface: http://localhost:57969")
    print("- Health Check: http://localhost:57969/health")

if __name__ == "__main__":
    main()

