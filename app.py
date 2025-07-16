import streamlit as st
import openai
import os
import json
from dotenv import load_dotenv

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

USER_DATA_FILE = "user_data.json"

st.set_page_config(page_title="Upwork Proposal Generator", page_icon="💼")
st.title("🤖 AI Proposal Writer for Upwork")

# Load saved data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "past_projects": "", "tech_tools": "", "name": "", "title": "",
        "job_success": "", "hourly_rate": "", "location": "", 
        "summary": "", "portfolio_links": ""
    }

# Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

# Load existing
user_data = load_user_data()

st.markdown("### 👤 Your Upwork Profile Info (optional but recommended)")

name = st.text_input("Your Name", value=user_data.get("name", "Muhammad Shakeel"))
title = st.text_input("Your Title", value=user_data.get("title", "AI Chatbot Developer | GPT-4, LangChain, RAG | FastAPI Expert"))
job_success = st.text_input("Job Success Score", value=user_data.get("job_success", "100%"))
hourly_rate = st.text_input("Your Rate", value=user_data.get("hourly_rate", "$10/hr"))
location = st.text_input("Location", value=user_data.get("location", "Burewala, Pakistan"))
summary = st.text_area("🔎 Summary / About You", value=user_data.get("summary", """🚀 Need a custom GPT chatbot or AI assistant that answers from your own data or automates tasks?
I build fast, scalable bots using GPT-4, LangChain, and FastAPI — tailored to your exact needs.

💼 Recently, I built an AI chatbot for a U.S. real estate firm that qualifies leads, gathers project details, and emails chat summaries — powered by OpenAI Assistants API and deployed on Hugging Face + Vercel.

⭐ With real-world client reviews, I deliver production-ready chatbots for SaaS, e-commerce, education, and legal platforms."""),
height=160)

portfolio_links = st.text_area("📎 Portfolio Links (1 per line)", value=user_data.get("portfolio_links", """https://revitalize-frontend.vercel.app/
https://aimlwithshakeel.site"""), height=100)

st.markdown("---")

# Proposal inputs
job_title = st.text_input("📌 Job Title")
job_description = st.text_area("📝 Full Job Description", height=200)
your_plan = st.text_area("🧠 Your Plan to Complete the Job", height=150)
past_projects = st.text_area("📁 Paste 3–5 Past Projects", value=user_data.get("past_projects", ""), height=180)
tech_tools = st.text_input("🛠️ Tools/Stack You’ll Use", value=user_data.get("tech_tools", ""))
delivery_time = st.text_input("⏳ Delivery Estimate (e.g., 5 days)")
tone = st.selectbox("✒️ Proposal Style", ["Friendly", "Expert", "Fast Delivery"])
save_data = st.checkbox("💾 Save Data for Next Time", value=True)

if "proposal_text" not in st.session_state:
    st.session_state.proposal_text = ""
if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = ""

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
You're an Upwork proposal expert.

Instructions:
- Use <200 words
- Use job post keywords
- Refer to relevant project
- Offer brief plan + 1 suggestion
- Ask 1 question
- Sound natural, not robotic
- Use tone: {tone}

=== JOB POST ===
Title: {job_title}
Description: {job_description}

=== FREELANCER PLAN ===
{your_plan}

=== PAST PROJECTS ===
{past_projects}

=== TOOLS ===
{tech_tools}

=== DELIVERY TIME ===
{delivery_time}

=== FREELANCER PROFILE ===
{profile_block}

Output:
FEEDBACK:
[your thoughts on the freelancer plan]
PROPOSAL:
[your winning proposal]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        feedback, proposal = "", ""

        if "FEEDBACK:" in content and "PROPOSAL:" in content:
            feedback = content.split("FEEDBACK:")[1].split("PROPOSAL:")[0].strip()
            proposal = content.split("PROPOSAL:")[1].strip()
        else:
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
        if all([job_title, job_description, your_plan]):
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
