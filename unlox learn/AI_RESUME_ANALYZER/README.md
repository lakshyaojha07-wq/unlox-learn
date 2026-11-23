# AI Resume Analyzer & Job Recommendation System

An NLP-based Streamlit application that helps students understand how well
their resume matches selected job roles. It provides a **match score**,
lists **missing skills**, and generates a simple **learning roadmap**.

## Features

- Upload a resume as **PDF or DOCX**.
- Automatic **text extraction and cleaning** (keeps technical tokens like
  `C++`, `C#`, `.NET` intact).
- **Skill extraction** against a controlled dictionary of 40+ technical
  skills, grouped into categories (Programming, Databases, ML, Cloud, Tools).
- **Match scoring** against 7 job roles using a blend of:
  - skill-overlap percentage (primary, easy to interpret), and
  - TF-IDF + cosine similarity (captures broader context).
- **Top-3 recommended roles**, ranked and charted.
- **Missing-skill analysis** for any selected target role.
- **Rule-based learning roadmap** (week-by-week) for closing skill gaps.
- **Downloadable analysis report** (`.txt`).

## Architecture / Workflow

```
Upload PDF or DOCX resume
        |
Extract resume text        (resume_parser.py)
        |
Clean and normalize text   (text_cleaner.py)
        |
Identify skills             (skill_extractor.py)
        |
Load job-role requirements  (data/job_roles.csv)
        |
Compare resume with each job role   (job_matcher.py)
        |
Calculate match scores
        |
Recommend roles
        |
Show missing skills and roadmap    (roadmap_generator.py)
        |
Streamlit dashboard + downloadable report   (app.py)
```

## Project Structure

```
ai_resume_analyzer/
|-- app.py                  # Streamlit dashboard (main entry point)
|-- resume_parser.py        # PDF/DOCX text extraction
|-- text_cleaner.py         # Text normalization
|-- skill_extractor.py      # Keyword-based skill detection
|-- job_matcher.py          # TF-IDF + cosine similarity, skill-overlap scoring
|-- roadmap_generator.py    # Rule-based learning roadmap
|-- requirements.txt
|-- README.md
|-- .env                    # Placeholder for optional LLM API keys
|-- .gitignore
|
|-- data/
|   |-- job_roles.csv           # 7 job roles + required skills
|   |-- skill_dictionary.csv    # ~40 skills, categorized, with aliases
|
|-- sample_resumes/         # Anonymized sample resume for testing
|
|-- reports/                # (empty) downloaded reports land here locally
|
|-- tests/
    |-- test_cases.csv      # Manual test tracking sheet
```

## Setup

1. **Clone the repository and install dependencies:**

   ```bash
   git clone <your-repo-url>
   cd ai_resume_analyzer
   pip install -r requirements.txt
   ```

2. **(Optional)** If you plan to add LLM-based feedback as an advanced
   feature, add API keys to `.env`. This is not required for the core app.

3. **Run the app:**

   ```bash
   streamlit run app.py
   ```

4. Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Usage

1. Upload a PDF or DOCX resume and click **Analyze Resume**.
2. Review the skills detected from your resume, grouped by category.
3. See your match score against all 7 job roles in the bar chart, plus your
   **top 3 recommended roles**.
4. Select a **target role** to see exactly which required skills you have
   and which are missing.
5. Follow the generated **week-by-week learning roadmap** for the missing
   skills.
6. Download a `.txt` analysis report to keep or share.

## How Matching Works (Beginner Approach)

- **Skill extraction:** the cleaned resume text is searched for each skill
  (and its aliases) in `data/skill_dictionary.csv` using word-boundary
  regex matching — this is fast, transparent, and easy for students to
  audit and extend.
- **Skill-overlap score:** `matched required skills / total required skills
  * 100`. This is the main number shown to students because it's the
  easiest to explain and debug.
- **TF-IDF + cosine similarity:** the resume text and a synthetic "job
  description" (the required skills joined into a sentence) are vectorized
  with `TfidfVectorizer` and compared with cosine similarity, adding a
  little more context-sensitivity beyond exact keyword hits.
- **Blended match score:** `0.7 * skill_score + 0.3 * tfidf_score`, used to
  rank roles.

### Adding job roles or skills

- Add a row to `data/job_roles.csv` with `job_role,required_skills`
  (comma-separated skill names that exist in `skill_dictionary.csv`).
- Add a row to `data/skill_dictionary.csv` with `skill,category,aliases`
  (pipe-separated aliases, e.g. `sklearn|scikit-learn`).

No code changes are required to extend either dataset.

## Advanced Improvements (Not Yet Implemented)

These are natural next steps, listed in the original project brief:

- spaCy-based entity/phrase extraction instead of pure keyword matching.
- Sentence Transformers for semantic (not just lexical) similarity.
- LLM-generated resume feedback via a controlled prompt (Groq/Gemini/OpenAI).
- FastAPI backend + database + Docker deployment.
- Resume section detection (education / skills / projects / experience).
- User login and saved report history.

## Responsible AI Notes

- This tool is for **guidance only** — not automated hiring or rejection.
- It scores only **job-related skills, education, projects, and experience**.
- It does **not** use gender, age, religion, nationality, photos, marital
  status, or disability in scoring.
- Match scores are **estimates**; a missing keyword does not always mean
  missing ability, and this tool should never be the sole basis for a
  hiring or rejection decision.
- Resumes are processed **in-session only** and are not stored permanently
  by the app itself.

## Testing

See `tests/test_cases.csv` for the manual test tracking sheet. Recommended
checks:

- Extraction quality on real PDF and DOCX resumes (including multi-column
  templates, which can be harder to extract cleanly).
- Skill precision/recall against a resume with a known skill list.
- Score consistency: adding/removing a skill from a resume should move the
  score in the expected direction.
- Graceful handling of scanned (image-only) PDFs — the app should show a
  clear error rather than crash, since `pypdf` cannot OCR images.

## License / Disclaimer

Built as an educational student project. Not intended for production
hiring decisions.
