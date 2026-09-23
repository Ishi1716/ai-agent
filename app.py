import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

from tools import calculator, get_current_time
from planner import decide_tool
from pdf_tool import search_pdf
from memory import ConversationMemory


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CHECK API KEY
# ============================================================

if not API_KEY:
    st.error(
        "❌ GEMINI_API_KEY not found.\n\n"
        "Please create a .env file in the project root "
        "and add your Gemini API key."
    )
    st.stop()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="My AI Agent",
    page_icon="🤖",
    layout="centered"
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 My AI Agent")

st.caption(
    "Gemini • Tools • PDF/RAG • Memory"
)


# ============================================================
# MEMORY
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

memory = st.session_state.memory


# ============================================================
# CLEAR CHAT
# ============================================================

if st.button("🗑️ Clear Conversation"):

    memory.clear()

    st.rerun()


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(question, context=None):

    try:

        # ----------------------------------------------------
        # PDF + RAG QUESTION
        # ----------------------------------------------------

        if context:

            prompt = f"""
You are a helpful AI assistant answering questions
using information retrieved from a DBMS PDF.

Use the PDF context below to answer the user's question.

PDF CONTEXT:
{context}

USER QUESTION:
{question}

Instructions:
- Answer clearly and accurately.
- Use simple language.
- Give a proper explanation.
- Use the PDF information when relevant.
- Do not invent information that is not supported
  by the provided context.
- If the context does not contain enough information,
  clearly say that.
"""

        # ----------------------------------------------------
        # NORMAL QUESTION
        # ----------------------------------------------------

        else:

            prompt = f"""
You are a helpful AI assistant.

Answer the following question clearly and simply.

USER QUESTION:
{question}
"""

        # ----------------------------------------------------
        # CALL GEMINI
        # ----------------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        # ----------------------------------------------------
        # GET RESPONSE
        # ----------------------------------------------------

        if response.text:
            return response.text

        return "⚠️ Gemini did not return a response."

    # --------------------------------------------------------
    # API ERROR
    # --------------------------------------------------------

    except Exception as e:

        error_message = str(e)

        # Rate limit / quota
        if "429" in error_message:

            return (
                "⚠️ Gemini is temporarily unavailable because "
                "the API rate limit has been reached.\n\n"
                "Your local AI Agent tools are still working. "
                "Please try Gemini again after the quota resets."
            )

        # API key error
        if "401" in error_message or "API key" in error_message:

            return (
                "❌ Gemini API key error.\n\n"
                "Please check your GEMINI_API_KEY in the "
                ".env file."
            )

        # Other errors
        return f"❌ Gemini error: {error_message}"


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in memory.get_history():

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["message"])

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):
            st.write(message["message"])


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask me anything..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_input:

    # --------------------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.write(user_input)

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    memory.add_message(
        "user",
        user_input
    )

    # --------------------------------------------------------
    # AGENT DECISION
    # --------------------------------------------------------

    tool_used = decide_tool(user_input)


    # ========================================================
    # CALCULATOR
    # ========================================================

    if tool_used == "calculator":

        st.info("🧮 Tool used: Calculator")

        result = calculator(user_input)

        response = f"Result: {result}"


    # ========================================================
    # CURRENT TIME
    # ========================================================

    elif tool_used == "get_current_time":

        st.info("🕐 Tool used: Current Time")

        result = get_current_time()

        response = f"Current time: {result}"


    # ========================================================
    # PDF + RAG
    # ========================================================

    elif tool_used == "pdf":

        st.info("📚 Tool used: PDF + RAG")

        # Search relevant information
        context = search_pdf(user_input)

        # Give retrieved information to Gemini
        response = ask_gemini(
            user_input,
            context
        )


    # ========================================================
    # GENERAL GEMINI
    # ========================================================

    else:

        st.info("🤖 Tool used: Gemini")

        response = ask_gemini(
            user_input
        )


    # ========================================================
    # SAVE AI RESPONSE
    # ========================================================

    memory.add_message(
        "assistant",
        response
    )


    # ========================================================
    # DISPLAY AI RESPONSE
    # ========================================================

    with st.chat_message("assistant"):
        st.write(response)