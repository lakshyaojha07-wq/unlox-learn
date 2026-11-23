"""
job_matcher.py
Module 5 & 6: Matching, Recommendation, and Skill-Gap Analysis

Two complementary scoring methods (per the project's "beginner approach"):

1. Skill-overlap score (primary, easy to explain to students):
   percentage of a role's required skills that were found in the resume.

2. TF-IDF + cosine similarity score (secondary/advanced):
   treats the resume text and a synthetic "job description" built from a
   role's required skills as documents, vectorizes them with TF-IDF, and
   compares them with cosine similarity. This captures some context beyond
   exact keyword hits.

The final displayed match score blends the two (weighted average), but both
are returned so the UI can show either or both.
"""

from pathlib import Path
from typing import List, Dict

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import parse_required_skills

DEFAULT_JOB_ROLES_PATH = Path(__file__).parent / "data" / "job_roles.csv"

# Weight given to skill-overlap vs TF-IDF cosine similarity in the blended score.
SKILL_WEIGHT = 0.7
TFIDF_WEIGHT = 0.3


def load_job_roles(path: Path = DEFAULT_JOB_ROLES_PATH) -> pd.DataFrame:
    """Load the job-role dataset (job_role, required_skills)."""
    return pd.read_csv(path)


def skill_overlap_score(resume_skills: List[str], required_skills: List[str]) -> float:
    """Percentage (0-100) of required skills that are present in the resume."""
    if not required_skills:
        return 0.0
    resume_set = {s.lower() for s in resume_skills}
    required_set = {s.lower() for s in required_skills}
    matched = resume_set & required_set
    return round(100 * len(matched) / len(required_set), 1)


def tfidf_similarity_score(resume_text: str, job_description: str) -> float:
    """Cosine similarity (0-100) between resume text and a job description."""
    if not resume_text.strip() or not job_description.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    except ValueError:
        # Happens if vocabulary is empty after stop-word removal.
        return 0.0
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(100 * float(similarity), 1)


def match_resume_to_roles(
    resume_text: str,
    resume_skills: List[str],
    job_roles_df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Score the resume against every job role in the dataset.

    Returns a DataFrame sorted by blended match score (highest first) with
    columns: job_role, required_skills, skill_score, tfidf_score,
    match_score, matched_skills, missing_skills.
    """
    if job_roles_df is None:
        job_roles_df = load_job_roles()

    rows = []
    for _, row in job_roles_df.iterrows():
        role = row["job_role"]
        required_skills = parse_required_skills(row["required_skills"])
        job_description = " ".join(required_skills)  # synthetic doc for TF-IDF

        s_score = skill_overlap_score(resume_skills, required_skills)
        t_score = tfidf_similarity_score(resume_text, job_description)
        blended = round(SKILL_WEIGHT * s_score + TFIDF_WEIGHT * t_score, 1)

        resume_set = {s.lower() for s in resume_skills}
        matched = [s for s in required_skills if s.lower() in resume_set]
        missing = [s for s in required_skills if s.lower() not in resume_set]

        rows.append(
            {
                "job_role": role,
                "required_skills": required_skills,
                "skill_score": s_score,
                "tfidf_score": t_score,
                "match_score": blended,
                "matched_skills": matched,
                "missing_skills": missing,
            }
        )

    result_df = pd.DataFrame(rows).sort_values("match_score", ascending=False).reset_index(drop=True)
    return result_df


def top_recommendations(ranked_df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Return the top-N recommended roles from an already-ranked DataFrame."""
    return ranked_df.head(n)


def get_role_details(ranked_df: pd.DataFrame, job_role: str) -> Dict:
    """Look up the scoring details for one specific role by name."""
    match = ranked_df[ranked_df["job_role"] == job_role]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()
