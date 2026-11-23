"""
skill_extractor.py
Module 3: Skill Extraction

Searches cleaned resume text for skills from a controlled dictionary
(data/skill_dictionary.csv) using keyword/alias matching, and groups
matches into categories (programming, databases, ML, cloud, tools).

spaCy or an LLM could be swapped in later as an "advanced improvement"
without changing the public interface of `extract_skills`.
"""

import re
from pathlib import Path
from collections import defaultdict

import pandas as pd

DEFAULT_DICTIONARY_PATH = Path(__file__).parent / "data" / "skill_dictionary.csv"


def load_skill_dictionary(path: Path = DEFAULT_DICTIONARY_PATH) -> pd.DataFrame:
    """Load the controlled skill list (skill, category, aliases)."""
    df = pd.read_csv(path)
    df["aliases"] = df["aliases"].fillna("")
    return df


def _build_pattern(skill: str, aliases: str) -> re.Pattern:
    """
    Build a case-insensitive regex that matches the skill name or any of
    its pipe-separated aliases as a whole word/phrase.

    text_cleaner.clean_text() strips hyphens/periods down to spaces (for
    everything except the protected tokens like C++, C#, .NET), so terms
    like "scikit-learn" must be matched as "scikit learn" against cleaned
    text. We normalize hyphens to a flexible space/hyphen pattern here so
    dictionary terms line up with however the cleaned text represents them.
    """
    terms = [skill] + [a for a in aliases.split("|") if a]
    escaped = []
    for t in terms:
        t = t.lower()
        # Escape first, then loosen escaped hyphens into "space or hyphen".
        e = re.escape(t).replace(r"\-", r"[\s-]")
        escaped.append(e)
    pattern = r"(?<![a-z0-9])(" + "|".join(escaped) + r")(?![a-z0-9])"
    return re.compile(pattern, flags=re.IGNORECASE)


def extract_skills(cleaned_text: str, dictionary: pd.DataFrame = None) -> dict:
    """
    Find which skills from the controlled dictionary appear in the resume.

    Args:
        cleaned_text: text already processed by text_cleaner.clean_text.
        dictionary: optional pre-loaded skill dictionary DataFrame.

    Returns:
        {
          "flat": ["Python", "SQL", ...],                # sorted list of matched skills
          "by_category": {"Programming": [...], "ML": [...], ...}
        }
    """
    if dictionary is None:
        dictionary = load_skill_dictionary()

    found = []
    by_category = defaultdict(list)

    for _, row in dictionary.iterrows():
        skill, category, aliases = row["skill"], row["category"], row["aliases"]
        pattern = _build_pattern(skill, aliases)
        if pattern.search(cleaned_text):
            found.append(skill)
            by_category[category].append(skill)

    return {
        "flat": sorted(found),
        "by_category": {cat: sorted(skills) for cat, skills in by_category.items()},
    }


def parse_required_skills(required_skills_str: str) -> list:
    """Split a comma-separated required-skills string from job_roles.csv into a list."""
    return [s.strip() for s in required_skills_str.split(",") if s.strip()]
