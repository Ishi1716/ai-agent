from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_text(text, chunk_size=800):

    chunks = []

    # Split PDF text into chunks
    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def search_chunks(chunks, question, top_k=2):

    if not chunks:
        return []

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    documents = chunks + [question]

    vectors = vectorizer.fit_transform(documents)

    # Compare question with PDF chunks
    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    )[0]

    # Sort from most relevant to least relevant
    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        # Only return chunks that actually have
        # some similarity with the question
        if similarities[index] > 0:

            results.append(chunks[index])

    return results