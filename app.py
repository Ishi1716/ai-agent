import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai

from tools import calculator, get_current_time
from planner import decide_tool
from pdf_tool import search_pdf
from memory import ConversationMemory


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="My AI Agent",
    page_icon="🤖",
    layout="centered"
)


# ============================================================
# GEMINI SETUP
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        API_KEY = None


client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        client = None


MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# MEMORY
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()


memory = st.session_state.memory


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(question, context=None):

    if client is None:
        return (
            "⚠️ Gemini is not configured right now. "
            "Please check the API configuration."
        )

    if context:

        prompt = f"""
You are an AI assistant answering questions using the provided document context.

Use the context below to answer the user's question.

If the answer is not available in the context, clearly say that the information
was not found in the provided document.

Keep the explanation simple and useful.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    else:

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and simply.

USER QUESTION:
{question}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "⚠️ Gemini did not return an answer."

    except Exception as e:

        error_text = str(e).lower()

        if "429" in error_text or "rate" in error_text or "quota" in error_text:
            return (
                "⚠️ Gemini is temporarily unavailable because "
                "the API usage limit has been reached.\n\n"
                "Your local AI Agent tools are still working. "
                "Please try Gemini again later."
            )

        if "503" in error_text or "unavailable" in error_text:
            return (
                "⚠️ Gemini is temporarily unavailable right now.\n\n"
                "Please try again in a little while."
            )

        return (
            "⚠️ Gemini is temporarily unavailable right now.\n\n"
            "Please try again later."
        )


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 My AI Agent")

st.caption(
    "Gemini • Tools • PDF/RAG • Memory"
)


# ============================================================
# CLEAR CONVERSATION
# ============================================================

if st.button("🗑️ Clear Conversation"):

    memory.clear()

    st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in memory.get_history():

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["message"])

    else:

        with st.chat_message("assistant"):
            st.write(message["message"])


# ============================================================
# USER INPUT
# ============================================================

user_input = st.chat_input("Ask me anything...")


if user_input:

    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    memory.add_message(
        "user",
        user_input
    )


    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.write(user_input)


    # --------------------------------------------------------
    # Decide which tool to use
    # --------------------------------------------------------

    tool = decide_tool(user_input)


    # ========================================================
    # CALCULATOR
    # ========================================================

    if tool == "calculator":

        result = calculator(user_input)

        tool_name = "🧮 Calculator"

        answer = f"Result: {result}"


    # ========================================================
    # CURRENT TIME
    # ========================================================

    elif tool == "get_current_time":

        result = get_current_time()

        tool_name = "🕐 Current Time"

        answer = f"Current time: {result}"


    # ========================================================
    # PDF + RAG
    # ========================================================

    elif tool == "pdf":

        context = search_pdf(user_input)

        tool_name = "📚 PDF + RAG"

        answer = ask_gemini(
            user_input,
            context
        )


    # ========================================================
    # GEMINI
    # ========================================================

    else:

        tool_name = "🤖 Gemini"

        answer = ask_gemini(
            user_input
        )


    # --------------------------------------------------------
    # Save assistant response
    # --------------------------------------------------------

    memory.add_message(
        "assistant",
        answer
    )


    # --------------------------------------------------------
    # Display tool used
    # --------------------------------------------------------

    st.info(
        f"🔧 Tool used: {tool_name}"
    )


    # --------------------------------------------------------
    # Display answer
    # --------------------------------------------------------

    with st.chat_message("assistant"):
        st.write(answer)