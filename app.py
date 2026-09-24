import os

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
# GEMINI API SETUP
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

# Streamlit Cloud Secrets
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
# CONVERSATION MEMORY
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()


memory = st.session_state.memory


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(question, context=None):

    # --------------------------------------------------------
    # Check API configuration
    # --------------------------------------------------------

    if client is None:
        return (
            "⚠️ Gemini is not configured right now.\n\n"
            "Please check the Gemini API configuration."
        )


    # --------------------------------------------------------
    # PDF / RAG prompt
    # --------------------------------------------------------

    if context:

        prompt = f"""
You are a helpful AI assistant answering questions using
the provided document context.

Use the document context to answer the user's question.

If the answer cannot be found in the document context,
say that the information was not found in the provided document.

Give a clear and simple explanation.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""


    # --------------------------------------------------------
    # Normal Gemini prompt
    # --------------------------------------------------------

    else:

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and simply.

USER QUESTION:
{question}
"""


    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

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


        # ----------------------------------------------------
        # Rate limit / quota
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "rate" in error_text
            or "quota" in error_text
        ):

            return (
                "⚠️ Gemini is temporarily unavailable because "
                "the API usage limit has been reached.\n\n"
                "Your local AI Agent tools are still working. "
                "Please try Gemini again later."
            )


        # ----------------------------------------------------
        # Service unavailable
        # ----------------------------------------------------

        if (
            "503" in error_text
            or "unavailable" in error_text
        ):

            return (
                "⚠️ Gemini is temporarily unavailable right now.\n\n"
                "Please try again in a little while."
            )


        # ----------------------------------------------------
        # Other Gemini errors
        # ----------------------------------------------------

        return (
            "⚠️ Gemini is temporarily unavailable right now.\n\n"
            "Please try again later."
        )


# ============================================================
# MEMORY SEARCH
# ============================================================

def get_name_from_memory():

    remembered_name = None

    for message in memory.get_history():

        if message["role"] != "user":
            continue

        previous_message = message["message"].strip()

        lower_message = previous_message.lower()

        if lower_message.startswith("my name is "):

            name = previous_message[11:].strip()

            if name:
                remembered_name = name.rstrip(".!?")

    return remembered_name


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
# DISPLAY PREVIOUS CONVERSATION
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
    # Agent decides which tool to use
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

        # Retrieve relevant information from the PDF
        context = search_pdf(user_input)

        tool_name = "📚 PDF + RAG"


        # Send retrieved context to Gemini
        gemini_answer = ask_gemini(
            user_input,
            context
        )


        # ----------------------------------------------------
        # RAG FALLBACK
        # ----------------------------------------------------

        if gemini_answer.startswith("⚠️ Gemini"):

            answer = (
                "📚 Relevant information found in your PDF:\n\n"
                + context
                + "\n\n"
                "ℹ️ Gemini is currently unavailable, so the "
                "retrieved PDF content is shown directly."
            )

        else:

            answer = gemini_answer


    # ========================================================
    # MEMORY
    # ========================================================

    else:

        lower_input = user_input.lower().strip()


        # ----------------------------------------------------
        # Store user's name
        # ----------------------------------------------------

        if lower_input.startswith("my name is "):

            name = user_input[11:].strip()

            name = name.rstrip(".!?")

            tool_name = "🧠 Conversation Memory"

            answer = (
                f"Nice to meet you, {name}! "
                "I'll remember your name during this conversation."
            )


        # ----------------------------------------------------
        # Retrieve user's name
        # ----------------------------------------------------

        elif (
            "what is my name" in lower_input
            or "what's my name" in lower_input
            or "do you remember my name" in lower_input
        ):

            remembered_name = get_name_from_memory()

            tool_name = "🧠 Conversation Memory"


            if remembered_name:

                answer = f"Your name is {remembered_name}."

            else:

                answer = (
                    "I don't know your name yet. "
                    "Tell me by saying: My name is ..."
                )


        # ----------------------------------------------------
        # General Gemini question
        # ----------------------------------------------------

        else:

            tool_name = "🤖 Gemini"

            answer = ask_gemini(
                user_input
            )


    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    memory.add_message(
        "assistant",
        answer
    )


    # ========================================================
    # DISPLAY TOOL USED
    # ========================================================

    st.info(
        f"🔧 Tool used: {tool_name}"
    )


    # ========================================================
    # DISPLAY ANSWER
    # ========================================================

    with st.chat_message("assistant"):
        st.write(answer)