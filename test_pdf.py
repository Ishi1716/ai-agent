import os

from dotenv import load_dotenv
from google import genai

from pdf_reader import read_pdf


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Read the PDF

pdf_text = read_pdf("pdfs/DBMS Notes.pdf")

# Ask the user
question = input("Ask a question about the PDF: ")


# Send PDF + question to Gemini
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=f"""
You are a helpful PDF assistant.

Use the PDF content below to answer the user's question.

PDF CONTENT:
{pdf_text}

USER QUESTION:
{question}

Answer clearly and briefly.

If the answer cannot be found in the PDF, say:
"I couldn't find that information in the PDF."
"""
)


print("\nAgent:", interaction.output_text)