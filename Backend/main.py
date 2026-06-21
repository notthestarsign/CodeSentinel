from pathlib import Path

from fastapi.responses import FileResponse
from groq import Groq
import os
import json
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, File, HTTPException, Form, UploadFile
import tempfile, zipfile, subprocess
from report_generator import generate_pdf_report
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CodeSentinel", description="AI-Powered Code Review Assistant", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', 
    '.h', '.cs', '.go', '.rb', '.php', '.html', '.css', '.scss', 
    '.json', '.yaml', '.yml', '.md', '.txt', '.rs', '.swift', 
    '.kt', '.vue', '.sql', '.sh', '.toml'
}

MAX_FILES = 15
MAX_FILE_SIZE = 50_000
MAX_TOTAL_CHARS = 24000

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def collect_code_files(directory: str) -> dict[str, str]:
    files = {}
    base = Path(directory)
    skip_dir = {'.git', 'node_modules', '__pycache__', ".venv", "venv", "dist", "build", ".next"}
    
    for path in sorted(base.rglob("*")):
        if any(skip in path.parts for skip in skip_dir):
            continue
        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            try:
                content = path.read_text(encoding='utf-8', errors="ignore")
                if len(content) <= MAX_FILE_SIZE:
                    rel = str(path.relative_to(base))
                    files[rel] = content
                    if len(files) >= MAX_FILES:
                        break
            except Exception:
                pass
    return files

def build_analysis_prompt(files: dict[str, str]) -> str:
    total = 0
    code_sections = []
    for filename, content in files.items():
        snippet = content[:1500] if len(content) > 1500 else content
        section = f"### FILE: {filename}\n```\n{snippet}\n```\n"
        if total + len(section) > MAX_TOTAL_CHARS:
            break
        code_sections.append(section)
        total += len(section)

    code_block = "\n".join(code_sections)

    return f"""You are an expert senior software engineer performing a comprehensive code review.
        Analyze the following codebase carefully and return a JSON object with this EXACT structure (no markdown, no explanation — pure JSON only):

        {{
        "summary": "2-3 sentence overview of what the codebase does and its overall quality",
        "overall_score": <integer 0-100>,
        "grade": "<A+|A|A-|B+|B|B-|C+|C|C-|D|F>",
        "stats": {{
            "files_analyzed": <int>,
            "total_issues": <int>,
            "critical_count": <int>,
            "warning_count": <int>,
            "info_count": <int>
        }},
        "bug_risks": [
            {{
            "severity": "<critical|warning|info>",
            "file": "<filename or 'General'>",
            "line_hint": "<line number or range if identifiable, else null>",
            "title": "<short issue title>",
            "description": "<detailed explanation>",
            "fix": "<concrete fix suggestion>"
            }}
        ],
        "security_concerns": [
            {{
            "severity": "<critical|warning|info>",
            "file": "<filename or 'General'>",
            "cwe": "<CWE-XXX or null>",
            "title": "<short title>",
            "description": "<detailed explanation>",
            "fix": "<concrete fix>"
            }}
        ],
        "complexity_warnings": [
            {{
            "severity": "<warning|info>",
            "file": "<filename>",
            "title": "<title>",
            "description": "<explanation>",
            "fix": "<suggestion>"
            }}
        ],
        "refactoring_suggestions": [
            {{
            "priority": "<high|medium|low>",
            "file": "<filename or 'General'>",
            "title": "<suggestion title>",
            "description": "<detailed description>",
            "benefit": "<why this improves the code>"
            }}
        ],
        "positive_highlights": [
            "<thing done well>",
            "<thing done well>"
        ],
        "tech_stack": ["<detected technology>"],
        "maintainability_score": <0-100>,
        "security_score": <0-100>,
        "performance_score": <0-100>,
        "test_coverage_note": "<observation about testing>"
        }}

        Return ONLY the JSON. No preamble. No explanation. No markdown fences.

        --- CODEBASE START ---
        {code_block}
        --- CODEBASE END ---
    """

async def analyze_with_ai(files: dict[str, str]) -> dict:
    prompt = build_analysis_prompt(files)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    result = json.loads(raw)
    result["files_reviewed"] = list(files.keys())
    return result

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Accept a zip file of code and analyze it."""
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, "Please upload a .zip file")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "upload.zip")
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)
            
        extract_dir = os.path.join(tmpdir, "code")
        os.makedirs(extract_dir)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
            
        files = collect_code_files(extract_dir)
        if not files:
            raise HTTPException(400, "No supported code files found in the zip file.")
        
        result = await analyze_with_ai(files)
        return result
    
@app.post("/analyze/github")
async def analyze_github(url: str = Form(...)):
    """Clone a public Github repo and analyze it."""
    if "github.com" not in url:
        raise HTTPException(400, "Please provide a valid Github URL.")
    
    #normalize url
    url = url.strip().rstrip("/")
    if not url.endswith(".git"):
        clone_url = url + ".git"
    else:
        clone_url = url
        
    with tempfile.TemporaryDirectory() as tmpdir:
        clone_dir = os.path.join(tmpdir, "repo")
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--single-branch", clone_url, clone_dir],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise HTTPException(400, f"Failed to clone repo: {result.stderr[:200]}")
        
        files = collect_code_files(clone_dir)
        if not files:
            raise HTTPException(400, "No supported code files found in the repository.")
        
        analysis = await analyze_with_ai(files)
        analysis["repo_url"] = url
        return analysis
    
@app.post("/report/pdf")
async def generate_report(analysis: dict):
    """Generate a PDF report from analysis data."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name
 
    generate_pdf_report(analysis, pdf_path)
 
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="code-review-report.pdf",
        headers={"Access-Control-Expose-Headers": "Content-Disposition"}
    )