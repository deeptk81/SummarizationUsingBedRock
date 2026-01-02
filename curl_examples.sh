
#!/bin/bash

# AI Web Content Summarizer - cURL Examples
# Make sure the server is running on port 57969

echo "🤖 AI Web Content Summarizer - cURL Examples"
echo "============================================="

# 1. Health Check
echo ""
echo "📋 1. Health Check"
echo "curl http://localhost:57969/health"
curl http://localhost:57969/health | python -m json.tool
echo ""

# 2. Basic Summarization
echo "📋 2. Basic URL Summarization"
echo "curl -X POST http://localhost:57969/summarize -H 'Content-Type: application/json' -d '{\"url\": \"https://en.wikipedia.org/wiki/Artificial_intelligence\"}'"
curl -X POST http://localhost:57969/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}' | python -m json.tool
echo ""

# 3. Federal Reserve Paper
echo "📋 3. Federal Reserve Research Paper"
echo "curl -X POST http://localhost:57969/summarize -H 'Content-Type: application/json' -d '{\"url\": \"https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm\"}'"
curl -X POST http://localhost:57969/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm"}' | python -m json.tool
echo ""

# 4. With timeout
echo "📋 4. With Timeout (60 seconds)"
echo "curl --max-time 60 -X POST http://localhost:57969/summarize -H 'Content-Type: application/json' -d '{\"url\": \"https://en.wikipedia.org/wiki/Machine_learning\"}'"
curl --max-time 60 -X POST http://localhost:57969/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Machine_learning"}' | python -m json.tool
echo ""

# 5. Error handling example (invalid URL)
echo "📋 5. Error Handling (Invalid URL)"
echo "curl -X POST http://localhost:57969/summarize -H 'Content-Type: application/json' -d '{\"url\": \"not-a-valid-url\"}'"
curl -X POST http://localhost:57969/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-valid-url"}' | python -m json.tool
echo ""

echo "✅ All cURL examples completed!"
echo "🌐 Web interface: http://localhost:57969"

