from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def search_chunks(chunks, question, top_k=3):

    vectorizer = TfidfVectorizer()

    documents = chunks + [question]

    vectors = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:
        results.append(chunks[index])

    return results