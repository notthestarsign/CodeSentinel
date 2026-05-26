# CodeSentinel — AI-Powered Code Review Assistant

An AI-powered code review tool that analyzes GitHub repositories or uploaded codebases
and produces professional reports covering bug risks, security vulnerabilities, complexity
warnings, and refactoring suggestions.

## Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| AI Analysis   | Groq API · Llama 3.3 70B          |
| Backend API   | Python · FastAPI · Uvicorn        |
| PDF Reports   | ReportLab                         |
| Repo cloning  | Git (subprocess)                  |
| Frontend      | HTML · CSS · Vanilla JS           |

---

## Quickstart

### 1. Prerequisites

- Python 3.10+
- Git installed and on PATH
- A Groq API key — get one free at https://console.groq.com

### 2. Clone & install

```bash
git clone <this-repo>
cd CodeSentinel/Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set your API key

Create a `.env` file inside `Backend/`:

```bash
GROQ_API_KEY=gsk_...your_key_here...
```

### 4. Start the backend

```bash
chmod +x start.sh
./start.sh
```

Or directly:

```bash
uvicorn main:app --reload --port 8000
```

API live at **http://localhost:8000** · Docs at **http://localhost:8000/docs**

### 5. Open the frontend

In a second terminal:

```bash
cd Frontend
python3 -m http.server 5500
```

Open **http://localhost:5500** in your browser.

---

## API Endpoints

### `GET /health`
Health check.

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

### `POST /analyze/github`
Analyze a public GitHub repository.

```bash
curl -X POST http://localhost:8000/analyze/github \
  -F "url=https://github.com/owner/repo"
```

### `POST /analyze/upload`
Analyze an uploaded `.zip` archive of code.

```bash
curl -X POST http://localhost:8000/analyze/upload \
  -F "file=@myproject.zip"
```

### `POST /report/pdf`
Generate a PDF report from analysis JSON.
```bash
curl -X POST http://localhost:8000/report/pdf \
  -H "Content-Type: application/json" \
  -d @analysis.json \
  --output report.pdf
```

---

## Analysis Output

```json
{
  "summary": "...",
  "overall_score": 74,
  "grade": "B",
  "maintainability_score": 70,
  "security_score": 55,
  "performance_score": 80,
  "stats": {
    "files_analyzed": 12,
    "total_issues": 9,
    "critical_count": 2,
    "warning_count": 5,
    "info_count": 2
  },
  "tech_stack": ["Python", "FastAPI"],
  "bug_risks": [ ... ],
  "security_concerns": [ ... ],
  "complexity_warnings": [ ... ],
  "refactoring_suggestions": [ ... ],
  "positive_highlights": [ ... ],
  "test_coverage_note": "..."
}
```

---

## Project Structure

```bash
CodeSentinel/
├── Backend/
│   ├── main.py               # FastAPI app + endpoints
│   ├── report_generator.py   # PDF report builder
│   ├── requirements.txt      # Python dependencies
│   ├── start.sh              # One-command startup script
│   └── .env                  # Not committed — add your key here
└── Frontend/
└── index.html            # Single-file HTML/CSS/JS frontend
```

---

## Limits & Notes

| Constraint             | Value                                                                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Max files per analysis | 15                                                                                                                                        |
| Max file size          | 50 KB per file                                                                                                                            |
| Max total chars to AI  | 24,000                                                                                                                                    |
| Max chars per file     | 1,500 (truncated)                                                                                                                         |
| Supported extensions   | `.py .js .ts .jsx .tsx .java .c .cpp .h .cs .go .rb .php .html .css .scss .json .yaml .yml .md .txt .rs .swift .kt .vue .sql .sh .toml` |
| GitHub repos           | Public only                                                                                                                               |

> Limits are set conservatively for Groq's free tier (12,000 TPM).
> Upgrade to Groq Dev tier or swap in a different provider to raise them.

---

## .gitignore

Make sure your `.env` is never committed
```bash
.env
venv/
pycache/
*.pyc
*.pdf
```

---

## Possible Future Features

- [ ] GitHub OAuth + private repo support
- [ ] Post review comments directly to Pull Requests via GitHub API
- [ ] Vector DB memory to track issues across multiple analyses
- [ ] GitHub Actions / CI integration
- [ ] Streaming analysis results via Server-Sent Events
- [ ] Side-by-side diff view for refactoring suggestions
- [ ] Support for Anthropic / OpenAI as alternative providers