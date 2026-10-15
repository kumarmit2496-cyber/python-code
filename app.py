import boto3
import streamlit as st
from botocore.exceptions import ClientError, NoCredentialsError

# ---------- Page setup ----------
st.set_page_config(page_title="Bedrock Chatbot", page_icon="🤖", layout="centered")

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; max-width: 800px;}
        .app-title {font-size: 2rem; font-weight: 700; margin-bottom: 0;}
        .app-sub {color: #8a8f98; margin-top: 0.2rem; margin-bottom: 1.2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Bedrock client (cached so it is created once) ----------
@st.cache_resource
def get_client(region: str):
    return boto3.client("bedrock-runtime", region_name=region)


# ---------- Sidebar: settings ----------
with st.sidebar:
    st.header("⚙️ Settings")
    region = st.text_input("AWS region", value="us-east-1")
    model_id = st.selectbox(
        "Model (must be enabled in your AWS account)",
        ["amazon.nova-micro-v1:0", "amazon.nova-lite-v1:0", "amazon.nova-pro-v1:0"],
    )
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, concise assistant.",
        height=100,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.05)
    max_tokens = st.slider("Max tokens", 100, 2000, 600, 50)
    stream = st.toggle("Stream response", value=True)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- Header ----------
st.markdown('<p class="app-title">🤖 Bedrock Chatbot</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="app-sub">Powered by Amazon Bedrock · <code>{model_id}</code></p>',
    unsafe_allow_html=True,
)

# ---------- Chat history ----------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": "..."}]

if not st.session_state.messages:
    st.info("👋 Ask me anything, for example: *What is Gen AI?*")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------- Bedrock helpers ----------
def build_request():
    """Convert chat history into the Bedrock Converse format."""
    request = {
        "modelId": model_id,
        "messages": [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in st.session_state.messages
        ],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
    }
    if system_prompt.strip():
        request["system"] = [{"text": system_prompt}]
    return request


def ask_bot():
    """Non-streaming: returns the full answer."""
    response = get_client(region).converse(**build_request())
    return response["output"]["message"]["content"][0]["text"]


def ask_bot_stream():
    """Streaming: yields text chunks as they arrive."""
    response = get_client(region).converse_stream(**build_request())
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            yield event["contentBlockDelta"]["delta"].get("text", "")


# ---------- Chat input ----------
if question := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            if stream:
                answer = st.write_stream(ask_bot_stream())
            else:
                with st.spinner("Thinking..."):
                    answer = ask_bot()
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except NoCredentialsError:
            st.error("AWS credentials not found. Run `aws configure` or set environment variables.")
            st.session_state.messages.pop()
        except ClientError as e:
            code = e.response["Error"]["Code"]
            st.error(f"Bedrock error ({code}): {e.response['Error']['Message']}")
            st.session_state.messages.pop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.session_state.messages.pop()
