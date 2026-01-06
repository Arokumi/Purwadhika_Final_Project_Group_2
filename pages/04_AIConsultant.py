# pages/04_AIConsultant.py
import streamlit as st
import requests


# ================================ Helper tool to make code readable ================================

def call_llm(api_url: str):
    try:
        response = requests.post(
            api_url, 
            json={
                "messages": st.session_state.consultant_messages,
                "session_id": st.session_state.session_id
                }
            ) 

    except Exception as e:
        st.error(f"Connection failed: {e}")

    return response


def show_steps(steps: list):
    html_content = ""
    
    with st.expander("See tool calling..."):
        for step in steps:

            tool_name = step.get("tool", "Unknown Tool")
            content = step.get("message", "")
            
            # append the HTML block for this step
            html_content += f"""
            <div class="tool-bubble">
                <div class="tool-header">
                    <span class="tool-icon">🛠️</span> 
                    {tool_name}
                </div>
                <div class="tool-content">{content}</div>
            </div>"""
        
        st.markdown(html_content, unsafe_allow_html=True)


# ================================ Main ================================
st.set_page_config(page_title="AI Career Consultant", layout="centered")
st.title("👨‍💼 AI Job Consultant")


# Global CSS
st.markdown(
    """
    <style>
    :root {
        --bg-main: #0b0f14;
        --bg-surface: #121826;
        --bg-card: #161d2f;

        --text-main: #e8ebf3;
        --text-muted: #9aa3b2;

        --accent: #6c8cff;
        --accent-hover: #7f9bff;
        --accent-soft: rgba(108, 140, 255, 0.15);

        --border-soft: rgba(255,255,255,0.06);
        --radius-lg: 18px;
        --radius-md: 14px;
    }

    /* App background */
    html, body, .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    /* Centered layout polish */
    .block-container {
        max-width: 900px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface);
        border-right: 1px solid var(--border-soft);
    }

    section[data-testid="stSidebar"] button {
        background: transparent;
        color: var(--text-muted);
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] button:hover,
    section[data-testid="stSidebar"] button[aria-selected="true"] {
        background-color: var(--accent-soft);
        color: var(--text-main);
        font-weight: 600;
    }

    /* Chat bubbles */
    .chat-user {
        background: var(--accent-soft);
        border-left: 3px solid var(--accent);
        border-radius: var(--radius-md);
        padding: 12px 14px;
        margin-bottom: 12px;
        font-size: 15px;
    }

    .chat-ai {
        background: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-md);
        padding: 12px 14px;
        margin-bottom: 12px;
        font-size: 15px;
    }

    /* Chat input */
    div[data-testid="stChatInput"] textarea {
        background-color: var(--bg-card);
        color: var(--text-main);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-soft);
        padding: 12px;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent);
        color: #0b0f14;
        border-radius: var(--radius-md);
        border: none;
        font-weight: 600;
        padding: 0.6rem 1.3rem;
    }

    .stButton > button:hover {
        background-color: var(--accent-hover);
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-md);
        color: var(--text-muted);
    }

    /* Tools history */
    .tool-bubble {
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        background-color: rgba(128, 128, 128, 0.05); /* Transparent grey */
    }
    .tool-header {
        font-weight: 600;
        font-size: 0.9rem;
        color: inherit;
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .tool-icon {
        margin-right: 6px;
        font-size: 1.1rem;
    }
    .tool-content {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 8px;
        border-radius: 6px;
        white-space: pre-wrap; /* Wraps long text/json */
        word-break: break-all;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Set local user variables
preference_job = st.session_state.get('prefered_jobs', {})
user_summary = st.session_state.get('user_summary', 'User has not provided a summary.')
user_name = st.session_state.get('user_name', 'John Doe')
current_job_title = preference_job.get('job_title', 'None')
last_job_title = st.session_state.get('last_consulted_job', None)

# if chatbot is processing data, disable user input
if "is_processing" not in st.session_state:
    print("--setting is_processing to False")
    st.session_state.is_processing = False


# if user select different prefered job, the system will delete previous chat history
if current_job_title != last_job_title:
    if 'consultant_messages' in st.session_state:
        print("--user changed jobs, deleting chat history")
        del st.session_state['consultant_messages']
    
    st.session_state['last_consulted_job'] = current_job_title
    st.session_state['is_processing'] = False


# system prompt
if "consultant_messages" not in st.session_state:
    st.session_state.consultant_messages = []
    print("--appending system prompts to messages")
    if current_job_title != "None":
        initial_context = f"""
        CONTEXT:
        {user_name} is looking for a job. Here is their profile summary:
        {user_summary}

        The User Prefered job is:
        Role: {preference_job.get('job_title', 'Not specified')}
        Company: {preference_job.get('company_name', 'Not specified')}

        The Job Description is:
        {preference_job.get('job_description', 'No description provided.')}
        
        YOUR TASK:
        You are a Career Consultant. If prompted, help them prepare to get their prefered job. 
        
        What you could do:
        - Tell them what skills they lack
        - what they should learn
        - what next steps by comparing their summary and the job description.
        """
        
        st.session_state.consultant_messages.append({"role": "system", "content": initial_context, "steps": []})
        st.session_state.consultant_messages.append({"role": "assistant", "content": f"Hey {user_name}! I see you want to apply for the **{preference_job.get('job_title')}** position at **{preference_job.get('company_name')}**. I have analyzed the job description. What would you like to know?", "steps": []})


# Prints messages according to role
print("\n\n======================= MESSAGES START HERE =======================")
for msg in st.session_state.consultant_messages:
    print(msg)
    role = msg["role"]
    if role != "system":
        with st.chat_message(role):
            steps = msg["steps"]
            if steps: show_steps(steps)
            st.markdown(msg["content"])
print("======================= MESSAGES END HERE =======================\n\n")

is_disabled = current_job_title == "None"
placeholder_text = "Select your prefered job first!" if is_disabled else "What skills should I learn?"

if is_disabled:
    st.warning("⚠️ You need to analyze your CV first AND select your prefered job to start consulting.")

input_disabled = is_disabled or st.session_state.is_processing


if prompt := st.chat_input(placeholder_text, disabled=input_disabled):
    print("--user inputted a prompt")
    st.session_state.is_processing = True

    st.session_state.consultant_messages.append({"role": "user", "content": prompt, "steps": []})

    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            API_URL = "http://localhost:8000/invoke-advisor" 
            response = call_llm(API_URL)

            if response.status_code == 200:
                reply = response.json()
                ans = reply.get("response", "Error")
                steps = reply.get("steps", [])

                if steps: show_steps(steps)
                st.markdown(ans)
                message = {"role": "assistant", "content": ans, "steps": steps if steps else []}
                st.session_state.consultant_messages.append(message)
            
            # Turn off the "busy" switch and refresh
            st.session_state.is_processing = False
            st.rerun()