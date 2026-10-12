
import streamlit as st
from pypdf import PdfReader
import re

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

st.title("AI Resume Screening System")
st.write("Resume Analysis, Skill Matching and Manual Comparison")

# ---------------- SKILLS DATABASE ----------------
SKILLS_LIST = [
    "Python", "Java", "SQL", "Machine Learning",
    "Deep Learning", "HTML", "CSS", "JavaScript",
    "C++", "C", "Django", "Flask", "Data Analysis",
    "Data Science", "Excel", "Power BI", "Tableau",
    "Communication", "Teamwork", "AWS", "Cloud Computing",
    "Git", "React", "Node.js", "PHP", "MongoDB",
    "MySQL", "Artificial Intelligence", "Operating Systems",
    "MS Office", "Problem Solving", "Leadership"
]


# ---------------- SKILL EXTRACTION ----------------
def extract_skills(text):
    found = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def normalize_skills(skills):
    return {skill.strip().lower() for skill in skills if skill.strip()}


# ---------------- RESUME MISTAKE CHECKER ----------------
def check_resume(text):
    mistakes = []
    lower_text = text.lower()

    # Basic resume section checks
    sections = {
        "Email address": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
        "Phone number": r"\b(?:\+?\d[\d\s()-]{8,}\d)\b"
    }

    for section, pattern in sections.items():
        if not re.search(pattern, text):
            mistakes.append(f"Check whether your {section} is included.")

    headings = [
        "education",
        "experience",
        "skills",
        "projects"
    ]

    missing_sections = [
        heading.title()
        for heading in headings
        if heading not in lower_text
    ]

    for section in missing_sections:
        mistakes.append(f"Resume may be missing a '{section}' section.")

    if len(text.split()) < 100:
        mistakes.append(
            "Resume text is short. Consider adding relevant details."
        )

    # Simple repeated-word check
    words = re.findall(r"\b[a-zA-Z]+\b", lower_text)
    repeated = sorted({
        words[i]
        for i in range(1, len(words))
        if words[i] == words[i - 1] and len(words[i]) > 2
    })

    for word in repeated:
        mistakes.append(f"Repeated word found: '{word}'.")

    if not mistakes:
        mistakes.append(
            "No basic issues detected. Please proofread your resume."
        )

    return mistakes


# ---------------- UPLOAD RESUME ----------------
st.header("1. Upload Resume PDF")

uploaded_file = st.file_uploader(
    "Choose your resume PDF",
    type=["pdf"],
    key="resume_upload"
)

resume_text = ""
resume_skills = []

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        resume_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        if resume_text.strip():
            st.success("Resume uploaded successfully!")

            resume_skills = extract_skills(resume_text)

            with st.expander("View Extracted Resume Text"):
                st.text(resume_text)

            st.write("**Skills detected in resume:**")
            st.write(", ".join(resume_skills) or "No supported skills found.")

        else:
            st.warning(
                "No selectable text found. This may be a scanned PDF."
            )

    except Exception as error:
        st.error(f"Could not read PDF: {error}")


# ---------------- MANUAL DETAILS ----------------
st.header("2. Enter Candidate and Manual Details")

name = st.text_input("Candidate Name", key="candidate_name")
qualification = st.text_input("Qualification", key="qualification")
experience = st.number_input(
    "Experience in years",
    min_value=0,
    max_value=50,
    value=0
)

manual_skills_text = st.text_input(
    "Enter Manual Skills (comma-separated)",
    placeholder="Python, SQL, Java",
    key="manual_skills"
)

manual_text = st.text_area(
    "Enter Resume Matter Manually (optional)",
    placeholder="Paste your resume summary, education, projects, experience..."
)


# ---------------- JOB REQUIREMENTS ----------------
st.header("3. Job Requirements")

required_skills_text = st.text_input(
    "Required Skills",
    value="Python, SQL, Machine Learning, Java"
)

important_skills_text = st.text_input(
    "Important Skills",
    value="Python, Machine Learning"
)

required_experience = st.number_input(
    "Required Experience in years",
    min_value=0,
    max_value=50,
    value=0
)


# ---------------- ANALYSIS ----------------
if st.button("Analyze Resume", type="primary"):

    job_skills = [
        skill.strip().lower()
        for skill in required_skills_text.split(",")
        if skill.strip()
    ]

    important_skills = normalize_skills(
        important_skills_text.split(",")
    )

    manual_skills = extract_skills(manual_skills_text)

    # Also support manually typed skills outside the database
    for skill in manual_skills_text.split(","):
        skill = skill.strip()
        if skill and skill.lower() not in normalize_skills(manual_skills):
            manual_skills.append(skill)

    if not job_skills:
        st.warning("Please enter at least one required skill.")

    elif not resume_text.strip() and not manual_skills_text.strip() and not manual_text.strip():
        st.warning("Upload a PDF or enter manual resume details.")

    else:
        # Use skills detected in the uploaded PDF
        resume_skill_set = normalize_skills(resume_skills)
        manual_skill_set = normalize_skills(manual_skills)

        # Match score for uploaded resume
        resume_matching = [
            skill for skill in job_skills
            if skill in resume_skill_set
        ]

        resume_missing = [
            skill for skill in job_skills
            if skill not in resume_skill_set
        ]

        # Match score for manually entered skills
        manual_matching = [
            skill for skill in job_skills
            if skill in manual_skill_set
        ]

        manual_missing = [
            skill for skill in job_skills
            if skill not in manual_skill_set
        ]

        total_weight = sum(
            2 if skill in important_skills else 1
            for skill in job_skills
        )

        def calculate_score(matched):
            earned = sum(
                2 if skill in important_skills else 1
                for skill in matched
            )
            return earned / total_weight * 100

        resume_skill_score = (
            calculate_score(resume_matching)
            if resume_text.strip() else None
        )

        manual_skill_score = (
            calculate_score(manual_matching)
            if manual_skills_text.strip() else None
        )

        # Experience score
        if required_experience == 0:
            experience_score = 100
        else:
            experience_score = min(
                experience / required_experience * 100,
                100
            )

        # Overall score based on skill match + experience
        resume_overall = (
            resume_skill_score * 0.8 + experience_score * 0.2
            if resume_skill_score is not None else None
        )

        manual_overall = (
            manual_skill_score * 0.8 + experience_score * 0.2
            if manual_skill_score is not None else None
        )

        # ---------------- RESULTS ----------------
        st.header("4. Resume Screening Results")

        st.write("**Candidate:**", name or "Not provided")
        st.write("**Qualification:**", qualification or "Not provided")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("PDF Resume Results")

            if resume_skill_score is not None:
                st.metric("Skill Match Score", f"{resume_skill_score:.1f}%")
                st.metric("Overall Resume Match Score", f"{resume_overall:.1f}%")

                st.write("**Matching Skills:**")
                st.write(", ".join(resume_matching) or "None")

                st.write("**Missing Skills:**")
                st.write(", ".join(resume_missing) or "None")

                st.progress(int(resume_skill_score))

        with col2:
            st.subheader("Manual Skills Results")

            if manual_skill_score is not None:
                st.metric("Skill Match Score", f"{manual_skill_score:.1f}%")
                st.metric("Overall Resume Match Score", f"{manual_overall:.1f}%")

                st.write("**Matching Skills:**")
                st.write(", ".join(manual_matching) or "None")

                st.write("**Missing Skills:**")
                st.write(", ".join(manual_missing) or "None")

                st.progress(int(manual_skill_score))
            else:
                st.info("Enter manual skills to compare.")

        # ---------------- DIFFERENCE ----------------
        st.header("5. Difference: PDF Resume vs Manual Skills")

        common_skills = sorted(resume_skill_set & manual_skill_set)
        only_resume = sorted(resume_skill_set - manual_skill_set)
        only_manual = sorted(manual_skill_set - resume_skill_set)

        diff1, diff2, diff3 = st.columns(3)

        with diff1:
            st.write("**Common Skills**")
            st.write(", ".join(common_skills) or "None")

        with diff2:
            st.write("**Only in PDF Resume**")
            st.write(", ".join(only_resume) or "None")

        with diff3:
            st.write("**Only in Manual Skills**")
            st.write(", ".join(only_manual) or "None")

        if resume_skill_score is not None and manual_skill_score is not None:
            difference = abs(resume_skill_score - manual_skill_score)
            st.info(f"Skill Match Score Difference: {difference:.1f} percentage points")

        # ---------------- MISTAKE CHECKER ----------------
        st.header("6. Resume Mistakes and Suggestions")

        if resume_text.strip():
            mistakes = check_resume(resume_text)

            for mistake in mistakes:
                st.warning(mistake)
        elif manual_text.strip():
            mistakes = check_resume(manual_text)

            for mistake in mistakes:
                st.warning(mistake)
        else:
            st.info("Upload a PDF or enter resume matter to check basic issues.")

        # ---------------- RECOMMENDATION ----------------
        st.header("7. Recommendation")

        score_to_use = (
            resume_overall
            if resume_overall is not None
            else manual_overall
        )

        if score_to_use is not None:
            if score_to_use >= 80:
                st.success("Strong Match")
            elif score_to_use >= 50:
                st.info("Moderate Match")
            else:
                st.error("Low Match")

        st.caption(
            "Scores are rule-based estimates, not a hiring decision. "
            "The mistake checker checks basic sections and repeated words; "
            "it does not provide full grammar or spelling correction."
        )



