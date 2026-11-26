
import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai

from tools import calculator, get_current_time
from pdf_tool import search_pdf
from memory import ConversationMemory


# ==================================================
# SETUP
# ==================================================

load_dotenv()

st.set_page_config(
    page_title="My AI Agent",
    page_icon="🤖",
    layout="centered"
)

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "messages" not in st.session_state:
    st.session_state.messages = []

memory = st.session_state.memory


# ==================================================
# GEMINI CLIENT
# ==================================================

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            return None

    return genai.Client(api_key=api_key)


def ask_gemini(question):
    client = get_gemini_client()

    if client is None:
        return (
            "Gemini API key is missing. "
            "Please check your .env file."
        )

    # Build conversation history
    conversation = ""

    for message in memory.get_history():
        conversation += (
            f'{message["role"]}: '
            f'{message["message"]}\n'
        )

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=f"""
You are a helpful AI assistant.

Answer the user's latest question clearly,
accurately, and in simple language.

Use the conversation history when relevant.
Do not invent facts.

Conversation history:
{conversation}

Latest question:
{question}
"""
    )

    answer = interaction.output_text

    memory.add_message("assistant", answer)

    return answer


# ==================================================
# TOOL ROUTING
# ==================================================

def get_calculation_expression(user_input):
    """
    Extract a mathematical expression only when the
    message is a calculation request or pure arithmetic.
    """

    text = user_input.strip()

    # Remove common calculation commands.
    text = re.sub(
        r"(?i)^\s*(calculate|compute|solve)\s+",
        "",
        text
    )

    text = text.replace(",", "").strip()

    # Accept arithmetic only, not ordinary sentences.
    if not re.fullmatch(
        r"[\d\s.+*/()%\-]+",
        text
    ):
        return None

    # Require at least one number and one operator.
    if not any(char.isdigit() for char in text):
        return None

    if not any(
        operator in text
        for operator in ["+", "-", "*", "/", "%"]
    ):
        return None

    return text


def is_time_request(text):
    """Identify common current-time questions."""

    patterns = [
        r"\bwhat(?:'s| is) the (?:current )?time\b",
        r"\bcurrent time\b",
        r"\btell me the time\b",
        r"\btime right now\b",
        r"\bwhat time is it\b"
    ]

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def is_pdf_question(text):
    """Identify questions likely related to the DBMS PDF."""

    keywords = [
        "dbms",
        "database",
        "normalization",
        "normal form",
        "sql",
        "transaction",
        "primary key",
        "foreign key",
        "acid properties",
        "indexing",
        "relational database"
    ]

    text = text.lower()

    return any(keyword in text for keyword in keywords)


# ==================================================
# APP HEADER
# ==================================================

st.title("🤖 My AI Agent")

st.write(
    "Your personal AI assistant powered by Gemini, "
    "with Calculator, Current Time, PDF/RAG and Memory."
)

with st.sidebar:
    st.header("🛠️ Available Tools")

    st.write("🧮 Calculator")
    st.write("🕐 Current Time")
    st.write("📚 PDF Question Answering / RAG")
    st.write("🤖 Gemini AI")
    st.write("🧠 Conversation Memory")

    st.divider()

    st.caption(
        "Built with Python, Streamlit and Gemini API."
    )


# ==================================================
# CLEAR CONVERSATION
# ==================================================

if st.button("🗑️ Clear Conversation"):
    memory.clear()
    st.session_state.messages = []
    st.rerun()


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# ==================================================
# PROCESS USER INPUT
# ==================================================

user_input = st.chat_input("Ask your AI agent...")

if user_input:

    # Display the user's message.
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    text = user_input.lower().strip()

    # Save the user's message to conversation memory.
    memory.add_message("user", user_input)

    response = ""
    tool_used = ""

    try:
        # ------------------------------------------
        # 1. CALCULATOR
        # ------------------------------------------

        expression = get_calculation_expression(user_input)

        if expression is not None:
            tool_used = "Calculator"

            result = calculator(expression)

            if (
                isinstance(result, str)
                and result.lower().startswith("invalid")
            ):
                response = (
                    "I couldn't calculate that expression. "
                    "Please enter a valid arithmetic expression."
                )
            else:
                response = f"Result: {result}"

        # ------------------------------------------
        # 2. CURRENT TIME
        # ------------------------------------------

        elif is_time_request(text):
            tool_used = "Current Time"

            result = get_current_time()

            response = f"Current time: {result}"

        # ------------------------------------------
        # 3. PDF / RAG
        # ------------------------------------------

        elif is_pdf_question(text):
            tool_used = "PDF / RAG"

            result = search_pdf(user_input)

            if result and result.strip():
                response = result
            else:
                response = (
                    "I couldn't find relevant information "
                    "in the available PDF documents. "
                    "Please check that the correct PDF is "
                    "available in your project."
                )

        # ------------------------------------------
        # 4. GEMINI AI
        # ------------------------------------------

        else:
            tool_used = "Gemini AI"
            response = ask_gemini(user_input)

    except Exception as error:
        error_text = str(error)
        lower_error = error_text.lower()

        if "429" in error_text or "quota" in lower_error:
            response = (
                "Gemini's API quota or rate limit was reached. "
                "Please try again later. Local tools may still "
                "be available."
            )

        elif (
            "api key" in lower_error
            or "authentication" in lower_error
            or "unauthorized" in lower_error
        ):
            response = (
                "Gemini authentication failed. "
                "Please check your GEMINI_API_KEY in .env."
            )

        else:
            response = (
                "Something went wrong while processing "
                "your request. Please try again."
            )

            st.error(f"Technical details: {error}")

    # ------------------------------------------
    # DISPLAY AND SAVE RESPONSE
    # ------------------------------------------

    if tool_used:
        st.caption(f"🔧 Tool used: {tool_used}")

    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Save local-tool responses to memory.
    # Gemini responses are already saved in ask_gemini().
    if tool_used != "Gemini AI":
        memory.add_message("assistant", response)
