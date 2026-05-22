stored_chunks = []


def store_chunks(chunks):
    global stored_chunks
    stored_chunks = chunks
    return len(stored_chunks)


def search_chunks(question: str, top_k: int = 5):
    question_words = set(question.lower().split())
    scored_chunks = []

    for chunk in stored_chunks:
        content = chunk["content"].lower()
        score = sum(1 for word in question_words if word in content)

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    return [chunk for score, chunk in scored_chunks[:top_k]]