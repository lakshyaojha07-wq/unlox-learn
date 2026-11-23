"""
app.py
Module 7: Streamlit Dashboard

Main entry point for the AI Resume Analyzer and Job Recommendation System.
Run with:  streamlit run app.py
"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from resume_parser import parse_resume, ResumeParsingError
from text_cleaner import clean_text
from skill_extractor import load_skill_dictionary, extract_skills
from job_matcher import load_job_roles, match_resume_to_roles, top_recommendations, get_role_details
from roadmap_generator import build_roadmap, format_roadmap_as_text

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "cleaned_text" not in st.session_state:
    st.session_state.cleaned_text = None
if "extracted" not in st.session_state:
    st.session_state.extracted = None
if "ranked_roles" not in st.session_state:
    st.session_state.ranked_roles = None
if "filename" not in st.session_state:
    st.session_state.filename = None

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📄 AI Resume Analyzer & Job Recommendation System")
st.caption(
    "Upload your resume to see how well it matches different job roles, "
    "what skills you're missing, and a simple roadmap to close the gap."
)

with st.expander("ℹ️ About this tool & responsible use", expanded=False):
    st.markdown(
        """
        - This tool is for **guidance only**, not automatic hiring or rejection.
        - It evaluates only **job-related skills, education, projects, and experience**.
        - It does **not** consider gender, age, religion, nationality, photos, marital
          status, or disability.
        - Match scores are **estimates** — a missing keyword does not always mean
          missing ability, and recruiters will look at much more than this score.
        - Your resume is processed **only for this session** and is not stored
          permanently.
        """
    )

# ---------------------------------------------------------------------------
# Module 1: Resume Upload
# ---------------------------------------------------------------------------
st.header("1. Upload your resume")
uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

col_a, col_b = st.columns([1, 1])
with col_a:
    analyze_clicked = st.button("Analyze Resume", type="primary", disabled=uploaded_file is None)
with col_b:
    if st.session_state.filename:
        st.write(f"Loaded file: **{st.session_state.filename}**")

if analyze_clicked and uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        with st.spinner("Extracting and analyzing resume..."):
            raw_text = parse_resume(uploaded_file.name, file_bytes)
            cleaned = clean_text(raw_text)
            skill_dict = load_skill_dictionary()
            extracted = extract_skills(cleaned, skill_dict)
            job_roles_df = load_job_roles()
            ranked = match_resume_to_roles(cleaned, extracted["flat"], job_roles_df)

        st.session_state.resume_text = raw_text
        st.session_state.cleaned_text = cleaned
        st.session_state.extracted = extracted
        st.session_state.ranked_roles = ranked
        st.session_state.filename = uploaded_file.name
        st.success("Resume analyzed successfully!")
    except ResumeParsingError as e:
        st.error(str(e))
    except Exception as e:  # pragma: no cover - safety net for the UI
        st.error(f"Something went wrong while analyzing the resume: {e}")

# ---------------------------------------------------------------------------
# Only show the rest once we have results
# ---------------------------------------------------------------------------
if st.session_state.extracted is not None and st.session_state.ranked_roles is not None:
    extracted = st.session_state.extracted
    ranked = st.session_state.ranked_roles

    # -----------------------------------------------------------------
    # Module 3: Extracted skills
    # -----------------------------------------------------------------
    st.header("2. Extracted Skills")
    if extracted["flat"]:
        for category, skills in extracted["by_category"].items():
            st.markdown(f"**{category}:** " + ", ".join(skills))
    else:
        st.warning(
            "No skills from the controlled dictionary were detected. "
            "Try a resume with more explicit technology/tool names."
        )

    # -----------------------------------------------------------------
    # Module 5: Match score chart + recommended roles
    # -----------------------------------------------------------------
    st.header("3. Match Scores Across Job Roles")
    chart_df = ranked[["job_role", "match_score"]].copy()
    fig = px.bar(
        chart_df,
        x="match_score",
        y="job_role",
        orientation="h",
        range_x=[0, 100],
        labels={"match_score": "Match Score (%)", "job_role": "Job Role"},
        text="match_score",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏆 Top 3 Recommended Roles")
    top3 = top_recommendations(ranked, n=3)
    for _, row in top3.iterrows():
        st.markdown(f"- **{row['job_role']}** — {row['match_score']}% match")

    # -----------------------------------------------------------------
    # Module 6: Target role selection + skill gap + roadmap
    # -----------------------------------------------------------------
    st.header("4. Target Role: Missing Skills & Learning Roadmap")
    role_options = ranked["job_role"].tolist()
    target_role = st.selectbox("Select your target job role", role_options)

    details = get_role_details(ranked, target_role)
    if details:
        score_col, found_col, missing_col = st.columns(3)
        score_col.metric("Match Score", f"{details['match_score']}%")
        found_col.metric("Skills Found", len(details["matched_skills"]))
        missing_col.metric("Skills Missing", len(details["missing_skills"]))

        st.markdown(f"**Skills found for {target_role}:** " + (", ".join(details["matched_skills"]) or "None"))
        st.markdown(f"**Missing skills for {target_role}:** " + (", ".join(details["missing_skills"]) or "None — great match!"))

        roadmap = build_roadmap(details["missing_skills"])
        if roadmap:
            st.subheader("📅 Suggested Learning Roadmap")
            roadmap_df = pd.DataFrame(roadmap)
            st.table(roadmap_df.rename(columns={
                "week": "Week", "skill": "Skill", "topic": "Topic", "start_with": "Start With"
            }))

        # -------------------------------------------------------------
        # Downloadable report
        # -------------------------------------------------------------
        st.header("5. Download Analysis Report")
        found_lines = [f"- {s}" for s in details["matched_skills"]] or ["- None"]
        missing_lines = [f"- {s}" for s in details["missing_skills"]] or ["- None"]
        top_lines = [
            f"{i + 1}. {r['job_role']} - {r['match_score']}%"
            for i, r in enumerate(top3.to_dict("records"))
        ]
        report_lines = [
            "AI RESUME ANALYZER - ANALYSIS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Resume file: {st.session_state.filename}",
            "",
            f"Target Role: {target_role}",
            f"Match Score: {details['match_score']}%",
            "",
            "Skills Found:",
            *found_lines,
            "",
            "Missing Skills:",
            *missing_lines,
            "",
            "Top Recommended Roles:",
            *top_lines,
            "",
            "Suggested Roadmap:",
            format_roadmap_as_text(roadmap),
            "",
            "Note: This report is an estimate for guidance purposes only and",
            "is not a substitute for recruiter or professional judgment.",
        ]
        report_text = "\n".join(report_lines)
        st.download_button(
            "⬇️ Download Report (.txt)",
            data=report_text,
            file_name=f"resume_analysis_{target_role.replace(' ', '_')}.txt",
            mime="text/plain",
        )

st.divider()
st.caption("Built as a student NLP project — matching is estimate-based and should not be used for automated hiring decisions.")
