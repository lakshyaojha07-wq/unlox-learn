"""
roadmap_generator.py
Module 6 (cont.): Skill-Gap Analysis -> Learning Roadmap

Generates a simple, rule-based, week-by-week learning roadmap for the
skills a student is missing for their target role. Each missing skill
gets a short description and a suggested starting resource/topic. This
is intentionally simple (no ML) per the project's "beginner approach";
it can be swapped for an LLM-generated version later as an advanced
feature.
"""

from typing import List, Dict

# Short topic + starting point for each known skill. Skills not listed
# here fall back to a generic template.
SKILL_LEARNING_GUIDE: Dict[str, Dict[str, str]] = {
    "Python": {"topic": "Python programming fundamentals", "start_with": "Python syntax, data structures, and functions"},
    "SQL": {"topic": "SQL querying", "start_with": "SELECT, JOIN, GROUP BY, and basic query optimization"},
    "Excel": {"topic": "Excel for data analysis", "start_with": "Pivot tables, VLOOKUP/XLOOKUP, and charts"},
    "Power BI": {"topic": "Power BI dashboards", "start_with": "Data import, DAX basics, and report building"},
    "Pandas": {"topic": "Data manipulation with Pandas", "start_with": "DataFrames, filtering, and groupby operations"},
    "NumPy": {"topic": "Numerical computing with NumPy", "start_with": "Arrays, broadcasting, and vectorized operations"},
    "Matplotlib": {"topic": "Data visualization", "start_with": "Line/bar/scatter plots and subplots"},
    "Machine Learning": {"topic": "Machine learning fundamentals", "start_with": "Supervised learning, train/test splits, evaluation metrics"},
    "scikit-learn": {"topic": "scikit-learn", "start_with": "Building and evaluating a simple classifier"},
    "Deep Learning": {"topic": "Deep learning basics", "start_with": "Neural network fundamentals and backpropagation"},
    "TensorFlow": {"topic": "TensorFlow / Keras", "start_with": "Building and training a simple neural network"},
    "PyTorch": {"topic": "PyTorch", "start_with": "Tensors, autograd, and a basic training loop"},
    "CNN": {"topic": "Convolutional Neural Networks", "start_with": "Image classification with a small CNN"},
    "NLP": {"topic": "Natural Language Processing", "start_with": "Tokenization, embeddings, and text classification"},
    "Transformers": {"topic": "Transformer models", "start_with": "Attention mechanism and using a pretrained transformer"},
    "Hugging Face": {"topic": "Hugging Face ecosystem", "start_with": "Using pretrained models and pipelines"},
    "LLM": {"topic": "Large language models", "start_with": "Prompting, tokens, and basic LLM API usage"},
    "RAG": {"topic": "Retrieval-Augmented Generation", "start_with": "Vector search plus prompting an LLM with retrieved context"},
    "Computer Vision": {"topic": "Computer vision basics", "start_with": "Image processing fundamentals and OpenCV"},
    "OpenCV": {"topic": "OpenCV", "start_with": "Image loading, filtering, and basic object detection"},
    "YOLO": {"topic": "YOLO object detection", "start_with": "Running and fine-tuning a pretrained YOLO model"},
    "Docker": {"topic": "Containerization with Docker", "start_with": "Writing a Dockerfile and running a container"},
    "Kubernetes": {"topic": "Kubernetes basics", "start_with": "Pods, deployments, and services"},
    "FastAPI": {"topic": "Building APIs with FastAPI", "start_with": "Creating routes and a simple REST API"},
    "REST APIs": {"topic": "REST API design", "start_with": "HTTP methods, status codes, and building a basic API"},
    "MLflow": {"topic": "ML experiment tracking with MLflow", "start_with": "Logging params, metrics, and models"},
    "Git": {"topic": "Version control with Git", "start_with": "Commits, branches, and pull requests"},
    "GitHub": {"topic": "GitHub collaboration", "start_with": "Repositories, issues, and pull requests"},
    "AWS": {"topic": "AWS cloud basics", "start_with": "Core services: S3, EC2, and IAM"},
    "PostgreSQL": {"topic": "PostgreSQL", "start_with": "Schema design and writing queries"},
}

GENERIC_GUIDE = {"topic": "this skill", "start_with": "an introductory tutorial or official documentation"}


def build_roadmap(missing_skills: List[str], weeks_per_skill: int = 1) -> List[Dict[str, str]]:
    """
    Build a simple week-by-week roadmap for a list of missing skills.

    Args:
        missing_skills: skills the student needs to learn for their target role.
        weeks_per_skill: how many weeks to allot per skill (default 1).

    Returns:
        List of {"week": "Week 1", "skill": "...", "topic": "...", "start_with": "..."}
    """
    roadmap = []
    week_num = 1
    for skill in missing_skills:
        guide = SKILL_LEARNING_GUIDE.get(skill, GENERIC_GUIDE)
        for _ in range(weeks_per_skill):
            roadmap.append(
                {
                    "week": f"Week {week_num}",
                    "skill": skill,
                    "topic": guide["topic"],
                    "start_with": guide["start_with"],
                }
            )
            week_num += 1
    return roadmap


def format_roadmap_as_text(roadmap: List[Dict[str, str]]) -> str:
    """Render a roadmap list as plain text, e.g. for a downloadable report."""
    if not roadmap:
        return "No missing skills detected — great match for this role!"
    lines = []
    for item in roadmap:
        lines.append(f"{item['week']}: {item['skill']} — {item['start_with']}")
    return "\n".join(lines)
