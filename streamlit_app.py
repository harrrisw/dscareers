import streamlit as st
import requests
import random
import time

# Sidebar background styling with semi-transparent overlay and white text
st.markdown(
    """
    <style>
    /* Sidebar background image */
    [data-testid="stSidebar"] {
        background-image: url(https://github.com/Reese0301/chatbot/blob/main/san-francisco1.jpg?raw=true);
        background-size: cover;
        color: white;
    }
    /* Semi-transparent overlay behind sidebar content */
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(0, 0, 0, 0.3); /* Black with 30% opacity */
        padding: 20px;
        border-radius: 10px;
    }
    /* Ensure all sidebar text is white */
    [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] ul, 
        [data-testid="stSidebar"] li, 
        [data-testid="stSidebar"] label {
            color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define API URLs for the Mentor and Expert models
API_URL_MENTOR = "https://flowise-arvh.onrender.com/api/v1/prediction/0647008b-1989-4d04-9e96-ba05c2c9cb91"
API_URL_EXPERT = "https://flowise-arvh.onrender.com/api/v1/prediction/1731ee13-cea5-499c-b2b1-94c7259a2721"

# List of randomized "thinking" messages
thinking_messages = [
    "Analyzing data patterns…",
    "Running a neural network… please hold.",
    "Processing large datasets… Taylor will be right back.",
    "Optimizing algorithms…",
    "Training the model… insights coming soon.",
    "Adjusting hyperparameters…",
    "Running a few more simulations… hang tight!",
    "Preparing a data-driven answer… patience is key.",
    "Just a moment… Taylor is cleaning the data.",
    "Extracting insights from data…"
]

# Initialize session state for chat messages, resume, and context if not already set
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm here to assist you with any data science career questions you may have. How can I help you today?"
    })
if "resume" not in st.session_state:
    st.session_state.resume = ""  # Placeholder for resume content

# Sidebar for model selector, additional inputs, and resume entry
with st.sidebar:
    model_choice = st.selectbox("Choose AI Model", options=["Mentor", "Expert (Experimental)"])

    if model_choice == "Mentor":
        outlook = st.select_slider("Outlook", options=["Pessimistic", "Practical", "Optimistic"], value="Practical")
        
        # Added "Default" option to the coaching style slider
        coaching_style = st.select_slider("Coaching Style", options=["Instructive", "Default", "Socratic"], value="Default")

        resume_text = st.text_area("Paste your resume here and upload with ↩️ if you’d like Taylor to remember your information for this session (Experimental Feature):")

        if st.button("↩️"):
            if resume_text.strip():  
                st.session_state.resume = resume_text
                st.success("Resume sent successfully!")
                st.session_state.messages.append({
                    "role": "system",
                    "content": "The user has uploaded their resume, which contains their information."
                })
            else:
                st.warning("No resume detected. Please paste your resume in the text area before sending.")
    else:
        st.session_state.resume = ""

    st.markdown(
        """
        <style>
        .suggested-prompts {
            background-color: rgba(240, 240, 245, 0.1);
            padding: 20px;
            border-radius: 10px;
            color: inherit;
        }
        .suggested-prompts h4, .suggested-prompts ul {
            color: inherit;
        }
        </style>
        
        <div class="suggested-prompts">
            <h4>💡 Suggested Prompts</h4>
            <ul>
                <li>What are the key steps to develop a career in data science?</li>
                <li>Surprise me with one insight on Data Science recruiting.</li>
                <li>What are the dos and don'ts of a data science interview?</li>
                <li>Can you suggest networking strategies for international students in data science?</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Feedback link section
    st.markdown(
        """
        <div style="margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; text-align: center;">
            <small style="color: white;">For Feedback or Concerns, contact: <a href="mailto:yizhuoyang@hotmail.com" style="color: white;">yizhuoyang@hotmail.com</a></small><br>
            <small><a href="https://docs.google.com/forms/d/e/1FAIpQLSelI6yZWQ4h0hWD7gSu6RzSwj-h_pSYkYT7Fdu2EHNgCkvQwA/viewform" target="_blank" style="color: white;">Feedback Form</a></small>
        </div>
        """,
        unsafe_allow_html=True
    )

# Function to send queries to the appropriate API based on model choice
def query(context, prompt, model, outlook=None, coaching_style=None):
    api_url = API_URL_MENTOR if model == "Mentor" else API_URL_EXPERT

    additional_metadata = ""
    if model == "Mentor":
        if outlook == "Pessimistic":
            additional_metadata += "ADOPT A REALISTIC AND CRITICAL TONE. ACKNOWLEDGE CHALLENGES AND POTENTIAL RISKS IN THE USER'S SITUATION, AND OFFER STRATEGIES TO MITIGATE THEM.\n"
        elif outlook == "Optimistic":
            additional_metadata += "ADOPT A POSITIVE AND ENCOURAGING TONE. EMPHASIZE POTENTIAL OPPORTUNITIES AND STRENGTHS IN THE USER'S SITUATION, AND OFFER STRATEGIES TO TAKE ADVANTAGE OF THEM.\n"
        
        # Only apply style instructions if not set to Default
        if coaching_style == "Instructive":
            additional_metadata += "USE A DIDACTIC TUTORING APPROACH. PROVIDE DETAILED, COMPREHENSIVE ANSWERS WITHOUT ASKING FOLLOW-UP QUESTIONS. FOCUS ON CLEARLY EXPLAINING CONCEPTS AND STRATEGIES TO THE USER.\n"
        elif coaching_style == "Socratic":
            additional_metadata += "After answering, use the Socratic method to ask the user one question to guide them toward deeper self-understanding of their situation and the data science industry.\n"

    context_with_resume = f"{st.session_state.resume}\n\n{context}" if st.session_state.resume else context
    full_context = f"{additional_metadata}{context_with_resume}"

    payload = {
        "question": f"{full_context}\n\nUser Question: {prompt}"
    }

    #Debugging output to check the payload before sending
    #st.write("(🚧You're seeing this message because a team member is in the debugging process🚧)", payload)
    
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        return response.json().get("text")
    else:
        return f"Error: {response.status_code}"

# Main content: Chat interface
home_title = "Taylor, Career Advisor in Data Science"
st.markdown(
    f"""<h1 style='display: inline;'>{home_title} <span style='color:#2E9BF5; font-size: 0.6em;'>Beta</span></h1>""",
    unsafe_allow_html=True
)
st.markdown(
    """
    ---
    - I am an AI Agent that answers your questions regarding Data Science careers and recruiting.
    - Built using a multiple-agent framework, I can deliver more accurate insights with sharper reasoning than ChatGPT. 
    - 🎓 **Mentor Mode**: I serve as your personal tutor, encouraging thoughtful reflection and helping you develop your career for continuous improvement.
    - 💯 **Expert Mode**: I deliver advanced, high-precision insights to address complex questions with maximum accuracy. (I will think longer, please be patient!)
    - 🏆 [**Interview Game**](#): Engage in a competitive interview simulation challenge against me.
    """
)

for message in st.session_state.messages:
    role = message["role"]
    avatar_url = "https://github.com/Reese0301/GIS-AI-Agent/blob/main/bear_714027.png?raw=true" if role == "assistant" else "https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"
    with st.chat_message(role, avatar=avatar_url):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"):
        st.markdown(prompt)

    thinking_message = random.choice(thinking_messages)
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(f"💭 **{thinking_message}**")

    start_time = time.time()
    
    CONTEXT_LIMIT = 5
    context = ""
    for msg in st.session_state.messages[-CONTEXT_LIMIT:]:
        if msg["role"] == "assistant":
            context += f"Assistant: {msg['content']}\n"
        elif msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "system":
            context += f"System: {msg['content']}\n"
    
    response_content = query(context, prompt, model_choice, outlook if model_choice == "Mentor" else None, coaching_style if model_choice == "Mentor" else None)
    
    end_time = time.time()
    response_time = end_time - start_time

    thinking_placeholder.empty()

    with st.chat_message("assistant", avatar="https://raw.githubusercontent.com/Reese0301/GIS-AI-Agent/refs/heads/main/bear_714027.png"):
        model_tag = "(Mentor)" if model_choice == "Mentor" else "(Expert)"
        st.markdown(f"💭 Thought for {response_time:.2f} seconds {model_tag}\n\n{response_content}")
    
    st.session_state.messages.append({"role": "assistant", "content": response_content})
