def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []

    if not text:
        return chunks

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append((start, end, chunk))

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks


def _line_number_at_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def chunk_repository_files(files):
    all_chunks = []

    for file in files:
        chunks = chunk_text(file["content"])

        for index, (start_offset, end_offset, chunk) in enumerate(chunks):
            all_chunks.append({
                "file_path": file["path"],
                "language": file["language"],
                "chunk_index": index,
                "start_line": _line_number_at_offset(file["content"], start_offset),
                "end_line": _line_number_at_offset(file["content"], end_offset),
                "content": chunk
            })

    return all_chunks
