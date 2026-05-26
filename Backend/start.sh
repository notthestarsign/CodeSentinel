#!/usr/bin/env bash
set -e

echo "──────────────────────────────────────"
echo "  CodeSentinel — AI Code Review"
echo "──────────────────────────────────────"

if [ -z "$GROQ_API_KEY" ]; then
  echo "  GROQ_API_KEY is not set."
  echo ""
  echo "    Get a free key at https://console.groq.com"
  echo "    Then either:"
  echo "      export GROQ_API_KEY=gsk_..."
  echo "    Or add it to Backend/.env"
  exit 1
fi

echo "  API key found"
echo "  Installing dependencies..."
pip install -r requirements.txt -q

echo "  Starting server on http://localhost:8000"
echo "    API docs: http://localhost:8000/docs"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload