from pdf_reader import read_pdf
from rag import split_text, search_chunks


# ============================================================
# LOAD PDF
# ============================================================

PDF_PATH = "pdfs/DBMS Notes.pdf"

pdf_text = read_pdf(PDF_PATH)

chunks = split_text(
    pdf_text,
    chunk_size=800
)


# ============================================================
# SEARCH PDF
# ============================================================

def search_pdf(question):

    results = search_chunks(
        chunks,
        question,
        top_k=2
    )

    if not results:

        return (
            "No relevant information was found "
            "in the PDF."
        )

    return "\n\n---\n\n".join(results)