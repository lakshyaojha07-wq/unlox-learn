"""
text_cleaner.py
Module 2: Text Extraction and Cleaning

Cleans raw resume text so it can be reliably compared against the skill
dictionary and job descriptions, while protecting technical tokens like
C++, C#, and .NET that would otherwise be mangled by naive symbol removal.
"""

import re

# Tokens that contain punctuation with real technical meaning.
# We temporarily swap these for placeholders before stripping symbols,
# then restore them afterwards.
PROTECTED_TOKENS = {
    r"c\+\+": "__CPLUSPLUS__",
    r"c#": "__CSHARP__",
    r"\.net\b": "__DOTNET__",
    r"node\.js": "__NODEJS__",
    r"c/c\+\+": "__CCPLUSPLUS__",
}

RESTORE_MAP = {
    "__CPLUSPLUS__": "C++",
    "__CSHARP__": "C#",
    "__DOTNET__": ".NET",
    "__NODEJS__": "Node.js",
    "__CCPLUSPLUS__": "C/C++",
}


def clean_text(raw_text: str) -> str:
    """
    Lowercase, protect technical symbols, strip noise, and normalize
    whitespace in resume text.

    Args:
        raw_text: text as extracted from the resume file.

    Returns:
        Cleaned text, safe for keyword search and TF-IDF vectorization.
    """
    if not raw_text:
        return ""

    text = raw_text.lower()

    # Step 1: protect technical tokens like c++, c#, .net
    for pattern, placeholder in PROTECTED_TOKENS.items():
        text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)

    # Step 2: remove emails, URLs, and phone numbers (privacy + noise reduction)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\+?\d[\d\-\s()]{7,}\d", " ", text)

    # Step 3: remove punctuation/symbols except placeholders (underscores kept)
    # Note: placeholders are uppercase, so the character class must allow
    # both cases or they would be stripped out here.
    text = re.sub(r"[^a-zA-Z0-9_\s]", " ", text)

    # Step 4: collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Step 5: restore protected technical tokens (lowercased form is fine
    # for matching; skill_extractor handles case-insensitive comparison)
    for placeholder, original in RESTORE_MAP.items():
        text = text.replace(placeholder.lower(), original.lower())

    return text
