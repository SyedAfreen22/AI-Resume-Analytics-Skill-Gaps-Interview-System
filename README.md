# AI-Powered Resume Analytics, Skill Gap & Interview Readiness System

## Features
- PDF resume upload
- Resume text extraction
- Name/email/phone detection
- Role-based skill detection
- Skill match percentage
- Missing skill gap detection
- Resume quality score
- Interview readiness score
- Personalized learning plan
- Interview questions with suggested answers
- Optional Gemini AI resume review

## Setup on Windows

### 1. Open terminal in this folder
```bash
cd path\to\AI_Resume_Analytics_System
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate it
```bash
venv\Scripts\activate
```

### 4. Install packages
```bash
pip install -r requirements.txt
```

### 5. Optional Gemini setup
Copy `.env.example` to `.env` and replace:
```text
GEMINI_API_KEY=your_actual_key
```

### 6. Run
```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Project architecture

app.py
    ↓
utils.py
    ├── PDF extraction
    ├── resume information extraction
    ├── skill gap analysis
    ├── readiness scoring
    ├── learning plan
    └── interview question generation
          ↓
     Optional Gemini AI

## Important
This is an academic/resume project MVP. The scoring is a rule-based prototype, not a professional recruitment assessment.
