def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []

    if not text:
        return chunks

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks


def chunk_repository_files(files):
    all_chunks = []

    for file in files:
        chunks = chunk_text(file["content"])

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "file_path": file["path"],
                "language": file["language"],
                "chunk_index": index,
                "content": chunk
            })

    return all_chunks