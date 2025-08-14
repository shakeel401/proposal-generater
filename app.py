import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

# ===== Load API Key =====
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===== Neon DB credentials =====
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        cursor_factory=RealDictCursor
    )

def get_projects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, project_name, description FROM projects ORDER BY date_added DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ===== Streamlit UI =====
st.set_page_config(page_title="Proposal Generator", page_icon="💼", layout="wide")
st.title("💼 AI Proposal Generator")

# --- Fetch projects from DB ---
projects = get_projects()
project_options = {f"{p['project_name']}": p['description'] for p in projects}

selected_projects = st.multiselect(
    "📂 Select Projects to Include in Proposal",
    options=list(project_options.keys())
)

job_title = st.text_input("📌 Job Title")
job_description = st.text_area("📝 Full Job Description", height=200)
your_plan = st.text_area("🧠 Your Plan to Complete the Job", height=150)
delivery_time = st.text_input("⏳ Delivery Estimate (e.g., 5 days)")
tone = st.selectbox("✒️ Proposal Style", ["Friendly", "Expert", "Fast Delivery"])
word_limit = st.slider("📝 Proposal Length (words)", 100, 500, 200, step=50)
model_choice = st.selectbox("🧠 Model", ["gpt-4", "gpt-4o", "gpt-4o-mini"])

if "proposal_text" not in st.session_state:
    st.session_state.proposal_text = ""

# ===== Proposal generator =====
def generate_proposal():
    selected_details = "\n\n".join([f"- {name}: {desc}" for name, desc in project_options.items() if name in selected_projects])

    system_prompt = f"""
You are a highly skilled human freelancer writing an Upwork proposal.

Structure your proposal like this:
1. **Hook / First Line** — Write a short, catchy opener that grabs attention.
2. **Problem Understanding** — Rephrase what the client needs in your own words.
3. **Solution** — Explain exactly how you will solve it, step-by-step, in a clear and confident tone.
4. **Reference Past Work** — Naturally mention the selected past projects to show credibility.
5. **Closing** — Invite the client to reply by asking a thoughtful question.

Guidelines:
- Keep it under {word_limit} words.
- Sound like a real person, not AI-generated.
- Match the tone: {tone}.
- Use keywords from the job post naturally.
"""

    user_prompt = f"""
=== JOB POST ===
Title: {job_title}
Description: {job_description}

=== PLAN ===
{your_plan}

=== SELECTED PROJECTS ===
{selected_details}

=== DELIVERY TIME ===
{delivery_time}
"""

    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        st.session_state.proposal_text = response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating proposal: {e}")

# ===== Buttons =====
col1, col2 = st.columns(2)
with col1:
    if st.button("✍️ Generate Proposal"):
        if job_title and job_description and your_plan and selected_projects:
            generate_proposal()
        else:
            st.warning("⚠️ Please fill in job title, description, plan, and select at least one project.")
with col2:
    if st.button("🔁 Regenerate Proposal"):
        generate_proposal()

# ===== Output =====
if st.session_state.proposal_text:
    st.markdown("### 📄 Your Proposal")
    st.text_area("✅ Copy-Ready Proposal", value=st.session_state.proposal_text, height=300, key="proposal_box")
    st.download_button(
        label="📥 Download Proposal",
        data=st.session_state.proposal_text,
        file_name="proposal.txt",
        mime="text/plain"
    )
