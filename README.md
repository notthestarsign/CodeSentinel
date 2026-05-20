# AI Code Review Assistant

An AI-powered code review tool that analyzes GitHub repositories or uploaded codebases
and produces professional reports covering bug risks, security vulnerabilities, complexity
warnings, and refactoring suggestions.

## Stack

| Layer | Technology |
|-------|-----------|
| AI Analysis | |
| Backend API | |
| PDF Reports | |
| Repo cloning | |
| Frontend | |

---

## Quickstart

### 1. Prerequisites

- Python 3.10+
- Git installed and on PATH

### 2. Clone & install

```bash
git clone <this-repo>
pip install -r requirements.txt
```

### 3. Set your API key


### 4. Start the server


---

## API Endpoints

### `POST /analyze/github`
Analyze a public GitHub repository.


### `POST /analyze/upload`
Analyze an uploaded `.zip` archive of code.


### `POST /report/pdf`
Generate a PDF report from analysis JSON.


### `GET /health`
Health check — returns `{"status": "ok"}`.

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
  "tech_stack": ["Python", "FastAPI", "SQLite"],
  "bug_risks": [ ... ],
  "security_concerns": [ ... ],
  "complexity_warnings": [ ... ],
  "refactoring_suggestions": [ ... ],
  "positive_highlights": [ ... ],
  "test_coverage_note": "..."
}
```

---

## Frontend

The React frontend (`code-review-frontend.jsx`) is a self-contained component.

**To use it:**


---

## Limits & Notes

| Constraint | Value |
|-----------|-------|
| Max files per analysis | |
| Max file size | |
| Max total chars sent to AI | |
| Supported extensions | |
| GitHub repos | Public only (no auth) |

---

## Possible Future Features

- [ ] GitHub OAuth + private repo support
- [ ] Post review comments directly to Pull Requests via GitHub API
- [ ] Vector DB memory to track issues across multiple analyses
- [ ] GitHub Actions / CI integration (`code-review-action`)
- [ ] Streaming analysis results via Server-Sent Events
- [ ] Side-by-side diff view for refactoring suggestions