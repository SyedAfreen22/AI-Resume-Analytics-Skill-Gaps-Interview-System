import os
import re
from typing import List, Dict

from pypdf import PdfReader

# Optional Gemini import. The main project works without Gemini.
try:
    from google import genai
except Exception:
    genai = None


ROLE_SKILLS = {
    "Data Analyst": [
        "excel", "sql", "python", "pandas", "numpy", "matplotlib",
        "seaborn", "statistics", "power bi", "tableau", "data cleaning",
        "data visualization", "eda", "pivot table", "power query"
    ],
    "Data Scientist": [
        "python", "sql", "pandas", "numpy", "scikit-learn", "machine learning",
        "statistics", "matplotlib", "seaborn", "eda", "feature engineering",
        "model evaluation", "deep learning"
    ],
    "Data Engineer": [
        "python", "sql", "spark", "pyspark", "etl", "data pipeline",
        "airflow", "aws", "azure", "gcp", "hadoop", "kafka",
        "database", "data warehouse"
    ],
    "Software Developer": [
        "python", "java", "c++", "sql", "oops", "dsa", "git", "github",
        "html", "css", "javascript", "rest api", "database"
    ],
    "Python Developer": [
        "python", "oops", "git", "github", "sql", "rest api",
        "flask", "django", "fastapi", "database", "testing"
    ]
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from all pages of a PDF."""
    reader = PdfReader(pdf_path)
    text = []

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
            text.append(page_text)
        except Exception:
            continue

    return "\n".join(text)


def extract_resume_info(text: str) -> Dict[str, str]:
    """Extract simple contact information using regex."""
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone_match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    lines = [x.strip() for x in text.splitlines() if x.strip()]
    name = ""

    if lines:
        # Usually the first line is the candidate's name.
        candidate = lines[0]
        if len(candidate) <= 60 and not "resume" in candidate.lower():
            name = candidate

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else ""
    }


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def contains_skill(text: str, skill: str) -> bool:
    text = normalize(text)
    skill = skill.lower()

    # Word/phrase-aware matching.
    pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def calculate_skill_gap(resume_text: str, role: str) -> Dict:
    required = ROLE_SKILLS.get(role, [])
    found = [skill for skill in required if contains_skill(resume_text, skill)]
    missing = [skill for skill in required if skill not in found]

    match = round((len(found) / len(required)) * 100) if required else 0

    return {
        "required": required,
        "found": found,
        "missing": missing,
        "match_percent": match
    }


def calculate_readiness(resume_text: str, skill_result: Dict, role: str) -> Dict:
    words = len(resume_text.split())
    lower = normalize(resume_text)

    # Resume quality checks.
    sections = {
        "education": "education" in lower,
        "projects": "project" in lower,
        "experience": "experience" in lower or "internship" in lower,
        "certifications": "certification" in lower or "certificate" in lower,
        "contact": bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text))
    }

    section_score = sum(sections.values()) / len(sections) * 100
    skill_score = skill_result["match_percent"]

    # A reasonable resume length gets a small bonus.
    length_score = 100 if 250 <= words <= 1000 else 70 if words >= 150 else 40

    resume_score = round(
        section_score * 0.65 +
        length_score * 0.35
    )

    readiness_score = round(
        skill_score * 0.55 +
        resume_score * 0.45
    )

    suggestions = []

    if skill_result["missing"]:
        suggestions.append(
            "Learn the missing skills: " +
            ", ".join(skill_result["missing"][:6])
        )

    if not sections["projects"]:
        suggestions.append("Add at least one practical project with measurable results.")

    if not sections["experience"]:
        suggestions.append("Add internship, training, volunteering, or relevant practical experience when available.")

    if not sections["certifications"]:
        suggestions.append("Add relevant certifications after completing useful courses.")

    if not sections["education"]:
        suggestions.append("Add a clear Education section.")

    if not suggestions:
        suggestions.append("Maintain your skills and practice role-specific interview questions.")

    return {
        "score": max(0, min(100, readiness_score)),
        "skill_score": skill_result["match_percent"],
        "resume_score": max(0, min(100, resume_score)),
        "suggestions": suggestions
    }


QUESTION_BANK = {
    "Data Analyst": [
        {
            "question": "Tell me about yourself.",
            "answer": "I am a Data Science student interested in Data Analytics. I am building skills in Excel, SQL, Python, pandas, data visualization and statistics. I enjoy converting raw data into useful insights and I am currently improving my practical projects and communication skills.",
            "keywords": ["Data Science", "Excel", "SQL", "Python", "pandas", "analytics"]
        },
        {
            "question": "What is the difference between Excel and SQL?",
            "answer": "Excel is mainly used for spreadsheet-based analysis, calculations, visualization and reporting. SQL is used to retrieve, filter, join and aggregate data stored in relational databases.",
            "keywords": ["spreadsheet", "database", "query", "filter", "join"]
        },
        {
            "question": "What is data cleaning?",
            "answer": "Data cleaning is the process of identifying and fixing missing values, duplicates, incorrect formats, inconsistent values and invalid records before analysis.",
            "keywords": ["missing values", "duplicates", "format", "quality"]
        },
        {
            "question": "What is a pivot table?",
            "answer": "A pivot table is an Excel feature used to summarize and analyze large datasets by grouping values and calculating totals, averages, counts and other summaries.",
            "keywords": ["Excel", "summary", "grouping", "aggregation"]
        },
        {
            "question": "What is the difference between mean and median?",
            "answer": "Mean is the arithmetic average of values. Median is the middle value after sorting the data. Median is often better when the dataset contains extreme outliers.",
            "keywords": ["average", "middle", "outlier", "statistics"]
        },
        {
            "question": "What is SQL JOIN?",
            "answer": "A JOIN combines rows from two or more tables using a related column. Common joins are INNER JOIN, LEFT JOIN, RIGHT JOIN and FULL JOIN.",
            "keywords": ["SQL", "tables", "INNER JOIN", "LEFT JOIN"]
        },
        {
            "question": "What is pandas in Python?",
            "answer": "Pandas is a Python library used for data manipulation and analysis. It provides structures such as DataFrame and functions for filtering, grouping, cleaning and transforming data.",
            "keywords": ["Python", "DataFrame", "data analysis"]
        },
        {
            "question": "How do you handle missing values?",
            "answer": "First I identify the amount and pattern of missing data. Depending on the situation, I may remove records, fill values using mean or median, use a meaningful category, or investigate the source of the missing data.",
            "keywords": ["missing values", "mean", "median", "data cleaning"]
        },
        {
            "question": "What is data visualization?",
            "answer": "Data visualization represents information using charts and graphs so that trends, comparisons, patterns and outliers can be understood quickly.",
            "keywords": ["charts", "graphs", "trends", "patterns"]
        },
        {
            "question": "Why should we hire you as a fresher?",
            "answer": "I have a strong willingness to learn, a foundation in Data Science and practical interest in analytics. I am consistently building projects, improving technical skills and practicing communication. I can learn quickly and contribute with a problem-solving mindset.",
            "keywords": ["learning", "Data Science", "projects", "problem solving"]
        }
    ]
}


def generate_interview_questions(role: str, found_skills: List[str], count: int = 10):
    bank = QUESTION_BANK.get(role)

    if not bank:
        bank = [
            {
                "question": f"What is your understanding of {role}?",
                "answer": f"I understand that a {role} works with relevant technical tools and solves practical business or software problems. I am building the required skills through projects and practice.",
                "keywords": [role, "skills", "projects"]
            }
        ]

    # Prefer questions relevant to detected skills, then fill remaining.
    questions = bank[:count]

    if len(questions) < count:
        questions += bank[:count - len(questions)]

    return questions[:count]


def get_learning_plan(missing_skills: List[str], role: str):
    if not missing_skills:
        return [
            "Review your current skills and complete one end-to-end project.",
            "Practice SQL and Python interview questions.",
            "Build a dashboard and explain your insights.",
            "Practice HR and technical interview answers.",
            "Update your resume and LinkedIn with measurable project results."
        ]

    plan = []
    for skill in missing_skills[:7]:
        plan.append(f"Learn and practice {skill} with a small hands-on task.")

    return plan


def analyze_with_gemini(resume_text: str, role: str, missing_skills: List[str]) -> str:
    """Optional Gemini analysis. Requires GEMINI_API_KEY."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key is missing."

    if genai is None:
        return "Gemini package is not installed. Run: pip install google-genai"

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a professional resume reviewer.

Target role: {role}

Missing skills detected:
{", ".join(missing_skills)}

Resume:
{resume_text[:12000]}

Give a concise review with these headings:
1. Resume strengths
2. Weaknesses
3. Skill gaps
4. Project suggestions
5. Interview preparation
6. Three specific improvements

Do not invent experience or qualifications.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Gemini analysis failed: {e}"
