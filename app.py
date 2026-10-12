
import streamlit as st
import re
from pypdf import PdfReader
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

# Professional website styling
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fc;
}
[data-testid="stHeader"] {
    background-color: transparent;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
h1, h2, h3 {
    color: #17365d;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dce5f0;
}
.stButton > button {
    background-color: #17365d;
    color: white;
    border-radius: 8px;
    border: none;
}
[data-testid="stFileUploader"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #dce5f0;
}
</style>
""", unsafe_allow_html=True)

# Website heading
st.title("📄 AI Resume Screening System")
st.write(
    "A smart dashboard to compare candidate skills "
    "with job requirements."
)

st.divider()

# Job requirements sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Enter the skills required for the job.")

    required_input = st.text_area(
        "Required Skills",
        value="python, machine learning, sql, java",
        height=130,
        placeholder="Python, SQL, Java"
    )

    st.caption("Separate skills using commas.")

# Resume upload
st.subheader("📤 Upload Candidate Resume")

uploaded_file = st.file_uploader(
    "Choose a resume PDF",
    type=["pdf"]
)

if uploaded_file is None:
    st.info("Upload a PDF resume to begin screening.")

else:
    try:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        resume_text = ""

        for page in reader.pages:
            resume_text += page.extract_text() or ""

        if not resume_text.strip():
            st.error(
                "Unable to extract text. "
                "Please upload a text-based PDF."
            )
            st.stop()

        resume_lower = resume_text.lower()

        # Candidate details
        st.divider()
        st.subheader("👤 Candidate Information")

        candidate_name = st.text_input(
            "Candidate Name",
            placeholder="Enter candidate name"
        )

        # Education details
        st.subheader("🎓 Educational Qualifications")

        qualification = st.selectbox(
            "Highest Qualification",
            [
                "Select Qualification",
                "10th / SSC",
                "Intermediate / 12th",
                "Diploma",
                "B.Tech / B.E.",
                "B.Sc",
                "B.Com",
                "B.A.",
                "BCA",
                "MCA",
                "M.Tech / M.E.",
                "M.Sc",
                "MBA",
                "Ph.D.",
                "Other"
            ]
        )

        college = st.text_input(
            "College / University Name",
            placeholder="Enter college name"
        )

        specialization = st.text_input(
            "Branch / Specialization",
            placeholder="Example: Computer Science"
        )

        year_options = (
            ["Not selected"] +
            [str(year) for year in range(2020, 2031)]
        )

        graduation_year = st.selectbox(
            "Graduation Year",
            year_options
        )

        percentage = st.text_input(
            "Percentage / CGPA",
            placeholder="Example: 85% or 8.5 CGPA"
        )

        # Prepare required skills
        required_skills = list(dict.fromkeys(
            skill.strip().lower()
            for skill in required_input.split(",")
            if skill.strip()
        ))

        # Find skills present in the resume
        matching_skills = [
            skill for skill in required_skills
            if re.search(
                r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
                resume_lower
            )
        ]

        # Find missing required skills
        missing_skills = [
            skill for skill in required_skills
            if skill not in matching_skills
        ]

        # Calculate match percentage
        score = (
            round(
                len(matching_skills)
                / len(required_skills) * 100
            )
            if required_skills else 0
        )

        # Results dashboard
        st.divider()
        st.subheader("📊 Screening Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Skill Match Score", f"{score}%")

        with col2:
            st.metric("Matching Skills", len(matching_skills))

        with col3:
            st.metric("Missing Skills", len(missing_skills))

        st.progress(score / 100)

        if not required_skills:
            st.warning("Enter job requirements in the sidebar.")
        elif score >= 75:
            st.success("Strong skill match!")
        elif score >= 40:
            st.warning("Moderate skill match. Review missing skills.")
        else:
            st.error("Low skill match. Review candidate skills.")

        # Skills comparison
        st.divider()
        st.subheader("🔍 Skills Comparison")

        left, right = st.columns(2)

        with left:
            st.markdown("### ✅ Matching Skills")

            if matching_skills:
                for skill in matching_skills:
                    st.write(f"✓ {skill.title()}")
            else:
                st.write("No matching skills found.")

        with right:
            st.markdown("### ❌ Missing Skills")

            if missing_skills:
                for skill in missing_skills:
                    st.write(f"• {skill.title()}")
            else:
                st.write("All required skills were found.")

        # Required skills difference
        st.divider()
        st.subheader("📋 Job Requirements Analysis")

        st.write("**Required Job Skills**")
        st.write(
            ", ".join(skill.title() for skill in required_skills)
            or "No skills entered"
        )

        st.write("**Skills Found in Resume**")
        st.write(
            ", ".join(skill.title() for skill in matching_skills)
            or "None"
        )

        st.write("**Skills to Improve or Add**")
        st.write(
            ", ".join(skill.title() for skill in missing_skills)
            if missing_skills else "None"
        )

        # Final candidate report at the bottom
        st.divider()
        st.subheader("📄 Candidate Report")

        with st.container(border=True):
            st.markdown("### Candidate Summary")

            st.write(
                f"**Candidate Name:** "
                f"{candidate_name or 'Not entered'}"
            )

            st.write(
                f"**Highest Qualification:** "
                f"{qualification if qualification != 'Select Qualification' else 'Not selected'}"
            )

            st.write(
                f"**College / University:** "
                f"{college or 'Not entered'}"
            )

            st.write(
                f"**Branch / Specialization:** "
                f"{specialization or 'Not entered'}"
            )

            st.write(f"**Graduation Year:** {graduation_year}")

            st.write(
                f"**Percentage / CGPA:** "
                f"{percentage or 'Not entered'}"
            )

            st.write(f"**Resume File:** {uploaded_file.name}")

            st.metric("Final Skill Match", f"{score}%")

            st.markdown("**Matching Skills**")
            st.write(
                ", ".join(skill.title() for skill in matching_skills)
                or "None"
            )

            st.markdown("**Missing Skills**")
            st.write(
                ", ".join(skill.title() for skill in missing_skills)
                or "None"
            )

    except Exception as e:
        st.error(f"Could not process the PDF: {e}")

st.divider()
st.caption("AI Resume Screening System | Student Mini Project")
