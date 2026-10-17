
from pathlib import Path

import streamlit as st

from agent import answer_question
from document_reader import read_folder_documents, combine_document_text

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "documents"

st.set_page_config(
    page_title="Smart Documentation Q&A Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Smart Documentation Q&A Agent")
st.write(
    "Ask questions about documents stored in your documents folder. "
    "The app uses Groq AI to generate answers from the extracted content."
)

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def scan_documents():
    """Read supported documents from the documents folder."""
    with st.spinner("Scanning documents..."):
        results = read_folder_documents(str(DOCUMENTS_DIR))

    loaded = []
    errors = []

    for item in results:
        text = item.get("text", "")
        status = item.get("status", "")

        if text and text.strip():
            loaded.append({
                "filename": item.get("filename", "Unknown file"),
                "text": text
            })
        else:
            errors.append({
                "filename": item.get("filename", "Unknown file"),
                "status": status or "No text extracted"
            })

    st.session_state["loaded_documents"] = loaded
    st.session_state["document_errors"] = errors


if "loaded_documents" not in st.session_state:
    scan_documents()

if st.button("🔄 Rescan documents folder"):
    scan_documents()

documents = st.session_state.get("loaded_documents", [])

st.subheader("📂 Documents found")
st.caption(f"Folder: {DOCUMENTS_DIR}")

if documents:
    st.success(f"Loaded {len(documents)} document(s).")

    for document in documents:
        st.write(f"📄 {document['filename']}")
else:
    st.warning(
        "No readable documents found. Copy supported files into the "
        "documents folder and click Rescan documents folder."
    )

errors = st.session_state.get("document_errors", [])

if errors:
    with st.expander("Files that could not be read"):
        for item in errors:
            st.write(f"**{item['filename']}** — {item['status']}")

st.divider()
st.subheader("💬 Ask your documents")

question = st.text_area(
    "Enter your question",
    placeholder="Example: Summarize the main concepts in my documents.",
    height=100
)

if st.button("🤖 Get Answer", type="primary"):
    if not documents:
        st.error("No readable documents are loaded. Please check the folder.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        combined_text = "\n\n".join(
            f"DOCUMENT: {document['filename']}\n{document['text']}"
            for document in documents
        )

        with st.spinner("Groq AI is analyzing your documents..."):
            answer = answer_question(combined_text, question)

        st.subheader("📝 Answer")
        st.markdown(answer)

st.caption(
    "Tip: Add new files to the documents folder and click Rescan "
    "documents folder before asking questions about them."
)
