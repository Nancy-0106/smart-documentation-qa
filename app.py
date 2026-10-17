
import re
import streamlit as st
from document_reader import read_all_documents
from agent import answer_question


def local_search(document_text, question, top_k=3):
    """Find relevant document sections without using an API."""

    stop_words = {
        "what", "is", "are", "the", "a", "an", "in", "on", "of",
        "to", "for", "and", "or", "how", "does", "do", "explain",
        "describe", "with", "from", "this", "that", "it", "be"
    }

    keywords = {
        word.lower()
        for word in re.findall(r"[a-zA-Z0-9]+", question)
        if len(word) > 1 and word.lower() not in stop_words
    }

    if not keywords:
        return "Please enter a more specific question."

    chunks = re.split(r"(?=Page\s+\d+\s*:)", document_text, flags=re.I)

    if len(chunks) <= 1:
        chunks = [
            document_text[i:i + 2000]
            for i in range(0, len(document_text), 1700)
        ]

    scored_chunks = []

    for index, chunk in enumerate(chunks):
        words = {
            word.lower()
            for word in re.findall(r"[a-zA-Z0-9]+", chunk)
        }
        score = len(keywords.intersection(words))

        if score > 0:
            scored_chunks.append((score, index, chunk.strip()))

    if not scored_chunks:
        return (
            "No matching section was found in the extracted document text. "
            "Try using important keywords from your document."
        )

    scored_chunks.sort(key=lambda item: (-item[0], item[1]))

    results = []
    for score, index, chunk in scored_chunks[:top_k]:
        results.append(
            f"**Matching section {len(results) + 1}** "
            f"(keyword matches: {score})\n\n"
            f"{chunk[:1800]}"
        )

    return "\n\n---\n\n".join(results)


st.set_page_config(
    page_title="Smart Documentation Q&A Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Smart Documentation Q&A Agent")
st.write(
    "Upload your supported documents into the documents folder, "
    "then search their extracted content or ask the AI."
)

with st.spinner("Reading documents..."):
    documents = read_all_documents()

valid_documents = {
    name: content
    for name, content in documents.items()
    if content and not content.startswith("Error:")
}

if not valid_documents:
    st.error(
        "No readable documents found. Add a PDF, DOCX, XLSX, "
        "or supported image to the documents folder."
    )
    st.stop()

selected_document = st.selectbox(
    "Choose a document",
    list(valid_documents.keys())
)

mode = st.radio(
    "Choose answer mode",
    [
        "Local Search (works without API)",
        "AI Answer (Gemini + CrewAI)"
    ],
    index=0
)

question = st.text_area(
    "Enter your question",
    placeholder="Example: What are control statements in R?"
)

if st.button("Get Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        document_text = valid_documents[selected_document]

        if mode == "Local Search (works without API)":
            st.subheader("Relevant Document Sections")
            st.info(
                "Local search does not use Gemini or require API quota. "
                "It finds relevant text; it does not generate an AI explanation."
            )
            st.markdown(local_search(document_text, question))

        else:
            try:
                with st.spinner("Generating AI answer..."):
                    answer = answer_question(document_text, question)

                st.subheader("AI Answer")
                st.write(answer)

            except Exception as error:
                st.warning(
                    "The AI service is unavailable or its quota may be "
                    "exhausted. Showing local document search results instead."
                )
                st.subheader("Relevant Document Sections")
                st.markdown(local_search(document_text, question))
                st.caption(f"AI error: {error}")

with st.expander("View extracted document text"):
    st.text(valid_documents[selected_document][:10000])
