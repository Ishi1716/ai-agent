import os

from dotenv import load_dotenv
from google import genai

from pdf_reader import read_pdf
from rag import split_text, search_chunks


# Load API key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Read PDF
text = read_pdf("pdfs/DBMS Notes.pdf")


# Split PDF into chunks
chunks = split_text(text)

print("Number of chunks:", len(chunks))


# Ask question
question = input("\nAsk a question about the PDF: ")


# Retrieve relevant chunks
results = search_chunks(
    chunks,
    question,
    top_k=3
)


# Combine retrieved information
context = "\n\n".join(results)


# Send only relevant information to Gemini
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=f"""
You are a helpful PDF assistant.

Answer the user's question using ONLY the information
provided in the retrieved PDF sections.

RETRIEVED PDF SECTIONS:
{context}

USER QUESTION:
{question}

If the answer is not available in the retrieved sections,
say:

"I couldn't find that information in the PDF."

Give a clear and simple answer.
"""
)


print("\nAgent:", interaction.output_text)