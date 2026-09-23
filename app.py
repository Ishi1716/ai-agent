import os

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
    page_icon="🤖"
)


# ==================================================
# SESSION MEMORY
# ==================================================

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
        return None

    return genai.Client(
        api_key=api_key
    )


# ==================================================
# GEMINI FUNCTION
# ==================================================

def ask_gemini(question):

    client = get_gemini_client()

    if client is None:
        return (
            "Gemini API key is not configured. "
            "Please check your .env file."
        )

    # Save user message
    memory.add_message(
        "user",
        question
    )

    # Build conversation
    conversation = ""

    for message in memory.get_history():

        conversation += (
            message["role"]
            + ": "
            + message["message"]
            + "\n"
        )

    interaction = client.interactions.create(

        model="gemini-3.8-flash",

        input=f"""
You are a helpful AI assistant.

Use the conversation history to understand
the user's latest question.

Conversation history:
{conversation}

Answer the latest question clearly,
simply and accurately.
"""
    )

    answer = interaction.output_text

    # Save Gemini response
    memory.add_message(
        "assistant",
        answer
    )

    return answer


# ==================================================
# TITLE
# ==================================================

st.title("🤖 My AI Agent")

st.write(
    "Gemini + Calculator + Current Time + "
    "PDF/RAG + Memory"
)


# ==================================================
# CLEAR CONVERSATION
# ==================================================

if st.button("🗑️ Clear Conversation"):

    memory.clear()

    st.session_state.messages = []

    st.rerun()


# ==================================================
# DISPLAY PREVIOUS MESSAGES
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# ==================================================
# CHAT INPUT
# ==================================================

user_input = st.chat_input(
    "Ask your AI agent..."
)


# ==================================================
# PROCESS USER QUESTION
# ==================================================

if user_input:

    # ----------------------------------------------
    # Display user message
    # ----------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):

        st.write(user_input)


    text = user_input.lower().strip()


    try:

        # ==========================================
        # CALCULATOR
        # ==========================================

        if any(
            symbol in text
            for symbol in [
                "+",
                "-",
                "*",
                "/",
                "%"
            ]
        ):

            st.write(
                "🔧 Tool used: Calculator"
            )

            result = calculator(
                user_input
            )

            if result == "Invalid expression":

                response = (
                    "❌ Invalid mathematical expression."
                )

                st.error(response)

            else:

                response = f"Result: {result}"

                st.success(response)


        # ==========================================
        # CURRENT TIME
        # ==========================================

        elif "time" in text:

            st.write(
                "🔧 Tool used: Current Time"
            )

            result = get_current_time()

            response = (
                f"Current time: {result}"
            )

            st.success(response)


        # ==========================================
        # PDF / RAG
        # ==========================================

        elif any(
            keyword in text
            for keyword in [
                "dbms",
                "database",
                "normalization",
                "normal form",
                "sql",
                "transaction",
                "primary key",
                "foreign key",
                "acid",
                "index",
                "relational"
            ]
        ):

            st.write(
                "🔧 Tool used: PDF/RAG"
            )

            result = search_pdf(
                user_input
            )

            if not result.strip():

                response = (
                    "I couldn't find relevant "
                    "information in the PDF."
                )

                st.warning(response)

            else:

                response = result

                with st.chat_message("assistant"):

                    st.write(response)


        # ==========================================
        # GEMINI
        # ==========================================

        else:

            st.write(
                "🤖 Tool used: Gemini"
            )

            response = ask_gemini(
                user_input
            )

            with st.chat_message("assistant"):

                st.write(response)


        # ==========================================
        # SAVE LOCAL TOOL RESPONSE
        # ==========================================

        if not text.startswith("error"):

            # Gemini already saves its response
            # inside ask_gemini()

            if not (
                "🤖 Tool used: Gemini"
                in response
                if isinstance(response, str)
                else False
            ):

                pass


        # ==========================================
        # SAVE RESPONSE TO STREAMLIT CHAT
        # ==========================================

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


        # ==========================================
        # DISPLAY LOCAL TOOL RESPONSE
        # ==========================================

        if not any(
            keyword in text
            for keyword in [
                "dbms",
                "database",
                "normalization",
                "normal form",
                "sql",
                "transaction",
                "primary key",
                "foreign key",
                "acid",
                "index",
                "relational"
            ]
        ) and not (
            "time" in text
        ) and not any(
            symbol in text
            for symbol in [
                "+",
                "-",
                "*",
                "/",
                "%"
            ]
        ):

            # Gemini response already displayed
            pass

        elif not (
            any(
                keyword in text
                for keyword in [
                    "dbms",
                    "database",
                    "normalization",
                    "normal form",
                    "sql",
                    "transaction",
                    "primary key",
                    "foreign key",
                    "acid",
                    "index",
                    "relational"
                ]
            )
        ):

            with st.chat_message("assistant"):

                st.write(response)


    except Exception as error:

        error_text = str(error)

        # ==========================================
        # GEMINI QUOTA ERROR
        # ==========================================

        if "429" in error_text:

            response = (
                "⚠️ Gemini API quota has been exceeded. "
                "Your local Calculator, Time and PDF/RAG "
                "tools can still be used."
            )

            with st.chat_message("assistant"):

                st.warning(response)


        # ==========================================
        # API KEY ERROR
        # ==========================================

        elif (
            "API key" in error_text
            or "No API key" in error_text
        ):

            response = (
                "⚠️ Gemini API key is missing or invalid. "
                "Please check your .env file."
            )

            with st.chat_message("assistant"):

                st.error(response)


        # ==========================================
        # OTHER ERROR
        # ==========================================

        else:

            response = (
                "❌ Something went wrong while "
                "processing your request."
            )

            with st.chat_message("assistant"):

                st.error(response)

                st.caption(
                    f"Error details: {error}"
                )


        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("🛠️ Available Tools")

    st.write("🧮 Calculator")
    st.write("🕐 Current Time")
    st.write("📚 DBMS PDF / RAG")
    st.write("🤖 Gemini AI")
    st.write("🧠 Conversation Memory")

    st.divider()

    st.write(
        "Built with Python, Streamlit "
        "and Gemini API."
    )