import streamlit as st
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

USER_DATA_FILE = "user_data.json"

st.set_page_config(page_title="Upwork Proposal Generator", page_icon="💼")
st.title("🤖 AI Proposal Writer for Upwork")

# Load saved data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "past_projects": "", "tech_tools": "", "name": "Muhammad Shakeel",
        "title": "AI Chatbot Developer | GPT-4, LangChain, RAG | FastAPI Expert",
        "job_success": "100%", "hourly_rate": "$10/hr", "location": "Burewala, Pakistan",
        "summary": "🚀 Need a custom GPT chatbot or AI assistant that answers from your own data or automates tasks?\nI build fast, scalable bots using GPT-4, LangChain, and FastAPI — tailored to your exact needs.\n\n💼 Recently, I built an AI chatbot for a U.S. real estate firm that qualifies leads, gathers project details, and emails chat summaries — powered by OpenAI Assistants API and deployed on Hugging Face + Vercel.\n\n⭐ With real-world client reviews, I deliver production-ready chatbots for SaaS, e-commerce, education, and legal platforms.",
        "portfolio_links": "https://revitalize-frontend.vercel.app/\nhttps://aimlwithshakeel.site"
    }

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

user_data = load_user_data()

# UI Inputs
st.markdown("### 👤 Your Upwork Profile Info")

name = st.text_input("Your Name", value=user_data["name"])
title = st.text_input("Your Title", value=user_data["title"])
job_success = st.text_input("Job Success Score", value=user_data["job_success"])
hourly_rate = st.text_input("Your Rate", value=user_data["hourly_rate"])
location = st.text_input("Location", value=user_data["location"])
summary = st.text_area("🔎 Summary / About You", value=user_data["summary"], height=160)
portfolio_links = st.text_area("📎 Portfolio Links (1 per line)", value=user_data["portfolio_links"], height=100)

st.markdown("---")

job_title = st.text_input("📌 Job Title")
job_description = st.text_area("📝 Full Job Description", height=200)
your_plan = st.text_area("🧠 Your Plan to Complete the Job", height=150)
past_projects = st.text_area("📁 Paste 3–5 Past Projects", value=user_data["past_projects"], height=180)
tech_tools = st.text_input("🛠️ Tools/Stack You’ll Use", value=user_data["tech_tools"])
delivery_time = st.text_input("⏳ Delivery Estimate (e.g., 5 days)")
tone = st.selectbox("✒️ Proposal Style", ["Friendly", "Expert", "Fast Delivery"])
word_limit = st.slider("📝 Proposal Length (words)", min_value=100, max_value=500, value=200, step=50)
model_choice = st.selectbox("🧠 Choose Model", ["gpt-4", "gpt-4o", "gpt-4o-mini"])
save_data = st.checkbox("💾 Save Data for Next Time", value=True)

if "proposal_text" not in st.session_state:
    st.session_state.proposal_text = ""
if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = ""

# Proposal generator
def generate_proposal():
    profile_block = f"""
Upwork Profile:
Name: {name}
Title: {title}
Job Success: {job_success}
Rate: {hourly_rate}
Location: {location}
Summary: {summary}
Portfolio:
{portfolio_links}
"""

    prompt = f"""
You're an expert Upwork proposal writer.

Instructions:
- Start with a 2-line strong hook to grab attention
- Write a full proposal using less than {word_limit} words
- Use keywords from the job post
- Reference 1–2 relevant projects
- Offer a clear plan and one suggestion
- End with one question for the client
- Use tone: {tone}

=== JOB POST ===
Title: {job_title}
Description: {job_description}

=== PLAN ===
{your_plan}

=== PAST PROJECTS ===
{past_projects}

=== TOOLS ===
{tech_tools}

=== DELIVERY TIME ===
{delivery_time}

=== FREELANCER PROFILE ===
{profile_block}

Output Format:
FEEDBACK:
[short review of freelancer plan]

PROPOSAL:
[the generated proposal]
"""

    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if "FEEDBACK:" in content and "PROPOSAL:" in content:
            feedback = content.split("FEEDBACK:")[1].split("PROPOSAL:")[0].strip()
            proposal = content.split("PROPOSAL:")[1].strip()
        else:
            feedback = ""
            proposal = content

        st.session_state.proposal_text = proposal
        st.session_state.feedback_text = feedback

    except Exception as e:
        st.session_state.feedback_text = f"❌ Error: {e}"
        st.session_state.proposal_text = ""

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("✍️ Generate Proposal"):
        if job_title and job_description and your_plan:
            if save_data:
                save_user_data({
                    "past_projects": past_projects,
                    "tech_tools": tech_tools,
                    "name": name, "title": title,
                    "job_success": job_success, "hourly_rate": hourly_rate,
                    "location": location, "summary": summary,
                    "portfolio_links": portfolio_links
                })
            generate_proposal()
        else:
            st.warning("⚠️ Fill in all required fields.")
with col2:
    if st.button("🔁 Regenerate Proposal"):
        generate_proposal()

# Output
if st.session_state.feedback_text:
    st.markdown("### 💬 AI Feedback")
    st.info(st.session_state.feedback_text)

if st.session_state.proposal_text:
    st.markdown("### 📄 Your Proposal")
    st.text_area("✅ Ready to Copy", value=st.session_state.proposal_text, height=300, key="proposal_box")

    st.markdown("""
        <button onclick="navigator.clipboard.writeText(document.querySelector('textarea#proposal_box').value)"
        style="background-color:#4CAF50;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;margin-top:10px;">
        📋 Copy to Clipboard</button>
    """, unsafe_allow_html=True)

    st.download_button(
        label="📤 Export Proposal to TXT",
        data=st.session_state.proposal_text,
        file_name="upwork_proposal.txt",
        mime="text/plain"
    )
