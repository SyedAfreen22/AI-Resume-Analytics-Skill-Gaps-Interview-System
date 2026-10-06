import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from utils import (
    extract_text_from_pdf,
    extract_resume_info,
    calculate_skill_gap,
    calculate_readiness,
    generate_interview_questions,
    get_learning_plan,
    analyze_with_gemini,
)

# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* ---------- Main page ---------- */

    .main-title {
        font-size: 36px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #666666;
        margin-bottom: 30px;
    }

    /* ---------- KPI Cards ---------- */

    .kpi-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 22px 15px;
        text-align: center;
        min-height: 135px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .kpi-title {
        font-size: 14px;
        color: #666666;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: #222222;
    }

    .kpi-subtitle {
        font-size: 12px;
        color: #777777;
        margin-top: 5px;
    }

    /* ---------- Section headers ---------- */

    .section-title {
        font-size: 27px;
        font-weight: 750;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* ---------- Skill badges ---------- */

    .skill-found {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px;
        border-radius: 20px;
        background-color: #e8f5e9;
        color: #1b5e20;
        font-size: 13px;
        font-weight: 600;
    }

    .skill-missing {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px;
        border-radius: 20px;
        background-color: #ffebee;
        color: #b71c1c;
        font-size: 13px;
        font-weight: 600;
    }

    /* ---------- Info boxes ---------- */

    .info-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* ---------- Score ---------- */

    .score-big {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
    }

    /* ---------- Footer ---------- */

    .footer {
        text-align: center;
        color: #777777;
        font-size: 13px;
        padding: 25px;
        margin-top: 40px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_info" not in st.session_state:
    st.session_state.resume_info = {}

if "skill_result" not in st.session_state:
    st.session_state.skill_result = None

if "readiness" not in st.session_state:
    st.session_state.readiness = None

if "target_role" not in st.session_state:
    st.session_state.target_role = "Data Analyst"


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <div style="font-size:45px;">🤖</div>
        <h2>AI Resume Analytics</h2>
        <p style="color:#777;">Career Intelligence System</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.subheader("🧭 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard",
        "📄 Resume Analysis",
        "🎯 Skill Gap",
        "🎤 Interview Practice",
        "📚 Learning Roadmap",
        "📈 Progress Tracking",
        "ℹ️ About Project"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.subheader("🎯 Target Job Role")

target_role = st.sidebar.selectbox(
    "Select your target role",
    [
        "Data Analyst",
        "Data Scientist",
        "Data Engineer",
        "Software Developer",
        "Python Developer"
    ],
    index=0
)

st.session_state.target_role = target_role

st.sidebar.markdown("---")

st.sidebar.subheader("🤖 AI Settings")

use_gemini = st.sidebar.checkbox(
    "Enable Gemini AI",
    value=False
)

if use_gemini:
    if os.getenv("GEMINI_API_KEY"):
        st.sidebar.success("Gemini API connected")
    else:
        st.sidebar.warning("Gemini API key not found")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🤖 AI-Powered Resume Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Resume Intelligence • Skill Gap • Interview Readiness • Career Growth</div>',
    unsafe_allow_html=True
)


# =========================================================
# RESUME UPLOAD
# =========================================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📤 Resume")

    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    if uploaded_file:

        temp_path = Path("uploaded_resume.pdf")

        temp_path.write_bytes(
            uploaded_file.getbuffer()
        )

        try:

            with st.spinner("Reading resume..."):

                resume_text = extract_text_from_pdf(
                    str(temp_path)
                )

            if resume_text.strip():

                st.session_state.resume_text = resume_text

                st.session_state.resume_info = extract_resume_info(
                    resume_text
                )

                st.session_state.skill_result = calculate_skill_gap(
                    resume_text,
                    target_role
                )

                st.session_state.readiness = calculate_readiness(
                    resume_text,
                    st.session_state.skill_result,
                    target_role
                )

                st.success("Resume loaded!")

            else:

                st.error(
                    "Could not extract text from this PDF."
                )

        except Exception as e:

            st.error(
                f"Error reading resume: {e}"
            )


# =========================================================
# CHECK WHETHER RESUME EXISTS
# =========================================================

resume_available = bool(
    st.session_state.resume_text.strip()
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">🏠 Career Intelligence Dashboard</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.info(
            "👈 Upload your resume from the sidebar to start the analysis."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                """
                <div class="info-card">
                    <h3>📄 Resume Analysis</h3>
                    <p>
                    Extract resume information and evaluate
                    resume quality.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                """
                <div class="info-card">
                    <h3>🎯 Skill Gap</h3>
                    <p>
                    Compare your skills with the requirements
                    of your target job.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                """
                <div class="info-card">
                    <h3>🎤 Interview Readiness</h3>
                    <p>
                    Practice technical and HR interview
                    questions.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        skill_result = st.session_state.skill_result
        readiness = st.session_state.readiness

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------

        required = len(skill_result["required"])
        matched = len(skill_result["found"])
        missing = len(skill_result["missing"])
        compatibility = skill_result["match_percent"]

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">
                        Required Skills
                    </div>
                    <div class="kpi-value">
                        {required}
                    </div>
                    <div class="kpi-subtitle">
                        For {target_role}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">
                        Matched Skills
                    </div>
                    <div class="kpi-value">
                        {matched}
                    </div>
                    <div class="kpi-subtitle">
                        Skills detected
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">
                        Missing Skills
                    </div>
                    <div class="kpi-value">
                        {missing}
                    </div>
                    <div class="kpi-subtitle">
                        Skills to improve
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">
                        Skill Match
                    </div>
                    <div class="kpi-value">
                        {compatibility}%
                    </div>
                    <div class="kpi-subtitle">
                        Job compatibility
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # -------------------------------------------------
        # READINESS
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">🎯 Interview Readiness</div>',
            unsafe_allow_html=True
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            st.metric(
                "Overall Readiness",
                f"{readiness['score']}/100"
            )

        with r2:

            st.metric(
                "Skill Score",
                f"{readiness['skill_score']}/100"
            )

        with r3:

            st.metric(
                "Resume Score",
                f"{readiness['resume_score']}/100"
            )

        st.progress(
            readiness["score"] / 100
        )

        if readiness["score"] >= 80:

            st.success(
                "🟢 Excellent readiness! You are well prepared."
            )

        elif readiness["score"] >= 60:

            st.warning(
                "🟡 Good readiness. Improve your missing skills."
            )

        else:

            st.error(
                "🔴 More preparation is recommended."
            )

        # -------------------------------------------------
        # QUICK ACTIONS
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">🚀 Recommended Actions</div>',
            unsafe_allow_html=True
        )

        for suggestion in readiness["suggestions"]:

            st.write(
                "👉 " + suggestion
            )


# =========================================================
# RESUME ANALYSIS
# =========================================================

elif page == "📄 Resume Analysis":

    st.markdown(
        '<div class="section-title">📄 Resume Analysis</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.warning(
            "Please upload your resume from the sidebar."
        )

    else:

        info = st.session_state.resume_info
        resume_text = st.session_state.resume_text

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Name</div>
                    <div class="kpi-value" style="font-size:20px;">
                        {info.get("name") or "Not detected"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Email</div>
                    <div class="kpi-value" style="font-size:18px;">
                        {info.get("email") or "Not detected"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Phone</div>
                    <div class="kpi-value" style="font-size:18px;">
                        {info.get("phone") or "Not detected"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Word Count</div>
                    <div class="kpi-value">
                        {len(resume_text.split())}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        readiness = st.session_state.readiness

        st.subheader("📊 Resume Quality")

        st.progress(
            readiness["resume_score"] / 100
        )

        st.write(
            f"Resume Score: **{readiness['resume_score']}/100**"
        )

        st.subheader("📄 Extracted Resume Text")

        with st.expander("Click to view extracted text"):

            st.text_area(
                "Resume",
                resume_text,
                height=400
            )


# =========================================================
# SKILL GAP
# =========================================================

elif page == "🎯 Skill Gap":

    st.markdown(
        '<div class="section-title">🎯 Skill Gap Analysis</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.warning(
            "Please upload your resume from the sidebar."
        )

    else:

        result = st.session_state.skill_result

        required = len(result["required"])
        matched = len(result["found"])
        missing = len(result["missing"])
        match = result["match_percent"]

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Required Skills</div>
                    <div class="kpi-value">{required}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Matched Skills</div>
                    <div class="kpi-value">{matched}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Missing Skills</div>
                    <div class="kpi-value">{missing}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Skill Match</div>
                    <div class="kpi-value">{match}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # -------------------------------------------------
        # COMPATIBILITY
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">📊 Skill Compatibility</div>',
            unsafe_allow_html=True
        )

        st.progress(
            match / 100
        )

        if match >= 80:

            st.success(
                "🟢 Excellent skill compatibility."
            )

        elif match >= 60:

            st.warning(
                "🟡 Moderate skill gap. Keep improving."
            )

        else:

            st.error(
                "🔴 Large skill gap detected."
            )

        # -------------------------------------------------
        # MATCHED SKILLS
        # -------------------------------------------------

        st.subheader("✅ Skills Found in Resume")

        if result["found"]:

            html = ""

            for skill in result["found"]:

                html += (
                    f'<span class="skill-found">'
                    f'{skill}'
                    f'</span>'
                )

            st.markdown(
                html,
                unsafe_allow_html=True
            )

        else:

            st.info(
                "No matching skills were detected."
            )

        # -------------------------------------------------
        # MISSING SKILLS
        # -------------------------------------------------

        st.subheader("❌ Missing Skills")

        if result["missing"]:

            html = ""

            for skill in result["missing"]:

                html += (
                    f'<span class="skill-missing">'
                    f'{skill}'
                    f'</span>'
                )

            st.markdown(
                html,
                unsafe_allow_html=True
            )

        else:

            st.success(
                "🎉 No major missing skills detected!"
            )


# =========================================================
# INTERVIEW PRACTICE
# =========================================================

elif page == "🎤 Interview Practice":

    st.markdown(
        '<div class="section-title">🎤 Interview Practice</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.warning(
            "Upload your resume first."
        )

    else:

        result = st.session_state.skill_result

        st.write(
            f"Target Role: **{target_role}**"
        )

        st.write(
            "Practice these questions before your interview."
        )

        number = st.slider(
            "Number of questions",
            min_value=5,
            max_value=10,
            value=5
        )

        if st.button(
            "🎤 Generate Interview Questions",
            use_container_width=True
        ):

            with st.spinner(
                "Preparing interview questions..."
            ):

                questions = generate_interview_questions(
                    target_role,
                    result["found"],
                    number
                )

            for i, question in enumerate(
                questions,
                start=1
            ):

                with st.expander(
                    f"Question {i}: {question['question']}"
                ):

                    st.markdown(
                        "**💡 Suggested Answer**"
                    )

                    st.write(
                        question["answer"]
                    )

                    st.markdown(
                        "**🔑 Important Keywords**"
                    )

                    st.write(
                        ", ".join(
                            question["keywords"]
                        )
                    )


# =========================================================
# LEARNING ROADMAP
# =========================================================

elif page == "📚 Learning Roadmap":

    st.markdown(
        '<div class="section-title">📚 Personalized Learning Roadmap</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.warning(
            "Upload your resume first."
        )

    else:

        result = st.session_state.skill_result

        missing = result["missing"]

        st.write(
            f"### 🎯 Target Role: {target_role}"
        )

        if missing:

            st.write(
                "Based on your resume, focus on these areas:"
            )

        else:

            st.success(
                "Your major required skills are already present."
            )

        plan = get_learning_plan(
            missing,
            target_role
        )

        for i, item in enumerate(
            plan,
            start=1
        ):

            st.markdown(
                f"""
                <div class="info-card">
                    <h4>📅 Day {i}</h4>
                    <p>{item}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# PROGRESS TRACKING
# =========================================================

elif page == "📈 Progress Tracking":

    st.markdown(
        '<div class="section-title">📈 Progress Tracking</div>',
        unsafe_allow_html=True
    )

    if not resume_available:

        st.warning(
            "Upload your resume first."
        )

    else:

        readiness = st.session_state.readiness
        result = st.session_state.skill_result

        st.subheader("Your Current Progress")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Overall Readiness",
                f"{readiness['score']}%"
            )

            st.progress(
                readiness["score"] / 100
            )

        with col2:

            st.metric(
                "Skill Compatibility",
                f"{result['match_percent']}%"
            )

            st.progress(
                result["match_percent"] / 100
            )

        st.markdown("---")

        st.subheader("🎯 Areas to Improve")

        if result["missing"]:

            for skill in result["missing"]:

                st.checkbox(
                    f"Learn {skill}",
                    key=f"progress_{skill}"
                )

        else:

            st.success(
                "🎉 You have no major skill gaps!"
            )


# =========================================================
# ABOUT PROJECT
# =========================================================

elif page == "ℹ️ About Project":

    st.markdown(
        '<div class="section-title">ℹ️ About the Project</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        ### 🤖 AI-Powered Resume Analytics,
        ### Skill Gap & Interview Readiness System

        This project is designed to help students and job seekers
        evaluate their resumes and prepare for their target roles.

        ### 🔹 Main Features

        - 📄 Resume PDF analysis
        - 🧠 Resume information extraction
        - 🎯 Skill gap analysis
        - 📊 Skill compatibility score
        - 📈 Resume quality score
        - 🎤 Interview question practice
        - 📚 Personalized learning roadmap
        - 🤖 Optional Gemini AI analysis

        ### 🛠 Technologies

        **Python**

        **Streamlit**

        **PyPDF**

        **Regex / NLP techniques**

        **Gemini AI API**

        **HTML/CSS**

        ### 🎯 Target Users

        - College students
        - Fresh graduates
        - Job seekers
        - Data Science students
        - Data Analyst aspirants

        ### 💡 Project Objective

        The objective is to connect resume analysis,
        skill-gap identification and interview preparation
        into one career intelligence system.
        """,
        unsafe_allow_html=True
    )


# =========================================================
# GEMINI AI ANALYSIS
# =========================================================

if (
    use_gemini
    and resume_available
    and page in [
        "🏠 Dashboard",
        "📄 Resume Analysis"
    ]
):

    st.markdown("---")

    st.markdown(
        '<div class="section-title">✨ Gemini AI Resume Review</div>',
        unsafe_allow_html=True
    )

    if os.getenv("GEMINI_API_KEY"):

        if st.button(
            "🤖 Run Gemini AI Analysis",
            use_container_width=True
        ):

            with st.spinner(
                "Gemini AI is analyzing your resume..."
            ):

                result = analyze_with_gemini(
                    st.session_state.resume_text,
                    target_role,
                    st.session_state.skill_result["missing"]
                )

            st.markdown(
                result
            )

    else:

        st.warning(
            "Add GEMINI_API_KEY to your .env file to enable Gemini AI."
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        AI-Powered Resume Analytics • Skill Gap • Interview Readiness
        <br>
        Academic Data Science Project
    </div>
    """,
    unsafe_allow_html=True
)