def generate_answer(question: str, chunks):
    if not chunks:
        return "I could not find relevant code in the repository for this question."

    context = "\n\n".join(
        [f"File: {chunk['file_path']}\n{chunk['content'][:800]}" for chunk in chunks]
    )

    answer = f"""
Based on the retrieved code, here is a simple explanation:

Question: {question}

Relevant files:
{chr(10).join(set(chunk['file_path'] for chunk in chunks))}

Explanation:
The system found code related to your question in the files listed above.
In the next version, this response will be generated using an LLM with RAG.

Retrieved context preview:
{context[:1500]}
"""

    return answer