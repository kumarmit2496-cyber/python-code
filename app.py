import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

# ==================================================
# Load Environment Variables
# ==================================================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ==================================================
# Page Config
# ==================================================
st.set_page_config(
    page_title="ChatGPT Clone",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# Custom CSS — soft, light "modern chat" theme
# ==================================================
st.markdown(
    """
    <style>
        /* Overall app background — soft lavender/blue gradient, easy on the eyes */
        .stApp {
            background: linear-gradient(160deg, #f6f8ff 0%, #eef2fb 45%, #eaf4f0 100%);
            color: #2b2d3a;
        }

        /* Hide default streamlit chrome */
        #MainMenu, footer, header {visibility: hidden;}

        /* Title */
        .app-title {
            font-size: 2.1rem;
            font-weight: 800;
            background: linear-gradient(90deg, #6c63ff, #22b07d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        .app-subtitle {
            color: #6b6f85;
            font-size: 0.95rem;
            margin-top: 0;
            margin-bottom: 1.2rem;
        }

        /* Chat bubbles */
        .chat-row {
            display: flex;
            margin: 10px 0;
            align-items: flex-start;
        }
        .chat-row.user { justify-content: flex-end; }
        .chat-row.assistant { justify-content: flex-start; }

        .bubble {
            max-width: 72%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.55;
            font-size: 0.98rem;
            box-shadow: 0 3px 10px rgba(80, 90, 140, 0.10);
        }
        .bubble.user {
            background: linear-gradient(135deg, #7f7bff, #6c63ff);
            color: #ffffff;
            border-bottom-right-radius: 4px;
        }
        .bubble.assistant {
            background: #ffffff;
            color: #2b2d3a;
            border: 1px solid #e4e7f2;
            border-bottom-left-radius: 4px;
        }
        .avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            margin: 0 8px;
            flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(80, 90, 140, 0.15);
        }
        .avatar.user { background: #6c63ff; }
        .avatar.assistant { background: #22b07d; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e6e8f2;
        }
        section[data-testid="stSidebar"] * { color: #2b2d3a !important; }

        /* Sidebar text inputs / text area */
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #f6f8ff !important;
            border: 1px solid #dfe3f2 !important;
            border-radius: 10px !important;
            color: #2b2d3a !important;
        }

        /* Chat input box */
        .stChatInput textarea {
            background-color: #ffffff !important;
            color: #2b2d3a !important;
            border: 1px solid #dfe3f2 !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatInput"] {
            background-color: transparent !important;
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #7f7bff, #6c63ff);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: 0.2s;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 14px rgba(108, 99, 255, 0.35);
        }

        /* Error / warning boxes readable on light bg */
        div[data-testid="stAlert"] {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Sidebar — settings
# ==================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    model = st.selectbox(
        "Model",
        ["gpt-5-mini", "gpt-5", "gpt-4o", "gpt-4o-mini"],
        index=0,
    )

    system_prompt = st.text_area(
        "System instructions",
        value="You are a helpful, friendly assistant.",
        height=100,
    )

    st.markdown("---")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Built with Streamlit + OpenAI Responses API")

    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found. Add it to a .env file.")

# ==================================================
# OpenAI Client
# ==================================================
client = OpenAI(api_key=api_key) if api_key else None


def ask_gpt(conversation, model_name):
    """
    Calls the OpenAI Responses API with the full conversation history
    so the model has context of prior turns.
    """
    response = client.responses.create(
        model=model_name,
        input=conversation,
    )
    return response.output_text


# ==================================================
# Header
# ==================================================
st.markdown('<p class="app-title">💬 ChatGPT Clone</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-subtitle">Powered by the OpenAI Responses API — ask me anything.</p>',
    unsafe_allow_html=True,
)

# ==================================================
# Session State
# ==================================================
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# ==================================================
# Render chat history
# ==================================================
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        avatar = "🧑" if role == "user" else "🤖"
        if role == "user":
            st.markdown(
                f"""
                <div class="chat-row user">
                    <div class="bubble user">{content}</div>
                    <div class="avatar user">{avatar}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="chat-row assistant">
                    <div class="avatar assistant">{avatar}</div>
                    <div class="bubble assistant">{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==================================================
# Chat input
# ==================================================
user_input = st.chat_input("Message ChatGPT Clone...")

if user_input:
    if not client:
        st.error("Cannot reach OpenAI — please set OPENAI_API_KEY in your .env file and restart.")
    else:
        # 1. Save & show user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. Build conversation for the API (system prompt + full history)
        conversation = [{"role": "system", "content": system_prompt}] + st.session_state.messages

        # 3. Call the model with a spinner, then render
        with st.spinner("Thinking..."):
            try:
                reply = ask_gpt(conversation, model)
            except Exception as e:
                reply = f"⚠️ Error calling OpenAI API: {e}"

        # 4. Save assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()
