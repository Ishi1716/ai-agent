from pdf_reader import read_pdf
from rag import split_text, search_chunks


# Load the PDF once
pdf_text = read_pdf("pdfs/DBMS Notes.pdf")

# Split PDF into chunks
chunks = split_text(pdf_text)


def search_pdf(question):

    results = search_chunks(
        chunks,
        question,
        top_k=3
    )

    if not results:
        return "I couldn't find relevant information in the PDF."

    return "\n\n".join(results)