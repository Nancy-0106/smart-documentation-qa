
from pathlib import Path

import streamlit as st

from agent import answer_question
from document_reader import (
    read_folder_documents,
    read_uploaded_file,
)

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "documents"

SUPPORTED_TYPES = [
    "pdf",
    "docx",
    "xlsx",
    "pptx",
    "txt",
    "md",
    "py",
    "sql",
    "log",
    "json",
    "xml",
    "yaml",
    "yml",
    "ini",
    "cfg",
    "csv",
    "html",
    "htm",
    "css",
    "js",
    "ts",
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "webp",
]

st.set_page_config(
    page_title="Smart Documentation Q&A Agent",
    page_icon="📚",
    layout="wide",
)

st.title("Smart Documentation Q&A Agent")
st.write(
    "Upload documents from your computer or use documents "
    "stored in the application's documents folder. "
    "Ask questions and get answers using Groq AI."
)

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# READ DOCUMENTS FROM THE APPLICATION'S FOLDER
# --------------------------------------------------

def scan_documents():
    """Read supported files from the server-side documents folder."""

    with st.spinner("Scanning application documents folder..."):
        results = read_folder_documents(str(DOCUMENTS_DIR))

    loaded = []
    errors = []

    for item in results:
        text = item.get("text", "")
        filename = item.get("filename", "Unknown file")
        status = item.get("status", "")

        if text and text.strip():
            loaded.append({
                "filename": filename,
                "text": text,
                "source": "Application folder",
            })
        else:
            errors.append({
                "filename": filename,
                "status": status or "No text extracted",
            })

    st.session_state["loaded_documents"] = loaded
    st.session_state["document_errors"] = errors


if "loaded_documents" not in st.session_state:
    scan_documents()


# --------------------------------------------------
# FOLDER DOCUMENT CONTROLS
# --------------------------------------------------

with st.expander("Documents in the application folder", expanded=False):
    st.caption(f"Folder: {DOCUMENTS_DIR}")

    if st.button("Rescan application folder"):
        scan_documents()
        st.rerun()

    folder_documents = st.session_state.get(
        "loaded_documents", []
    )

    if folder_documents:
        st.success(
            f"{len(folder_documents)} document(s) loaded "
            "from the application folder."
        )

        for document in folder_documents:
            st.write(f"📄 {document['filename']}")
    else:
        st.info("No readable documents were found in this folder.")

    folder_errors = st.session_state.get(
        "document_errors", []
    )

    if folder_errors:
        with st.expander("Files that could not be read"):
            for item in folder_errors:
                st.write(
                    f"**{item['filename']}** — {item['status']}"
                )


# --------------------------------------------------
# BROWSER UPLOAD
# --------------------------------------------------

st.divider()
st.subheader("Upload your own documents")

st.write(
    "Select files from any folder on your computer. "
    "You can select multiple files at once."
)

uploaded_files = st.file_uploader(
    "Choose documents",
    type=SUPPORTED_TYPES,
    accept_multiple_files=True,
    help=(
        "Supported formats include PDF, Word, Excel, "
        "PowerPoint, text/code files, and images."
    ),
)

uploaded_documents = []
upload_errors = []

if uploaded_files:
    with st.spinner("Reading your uploaded documents..."):
        for uploaded_file in uploaded_files:
            text = read_uploaded_file(uploaded_file)

            filename = Path(uploaded_file.name).name

            if (
                text
                and text.strip()
                and not text.startswith("ERROR:")
                and not text.startswith("OCR ERROR:")
                and not text.startswith("IMAGE ERROR:")
            ):
                uploaded_documents.append({
                    "filename": filename,
                    "text": text,
                    "source": "Browser upload",
                })
            else:
                upload_errors.append({
                    "filename": filename,
                    "status": text or "No text could be extracted.",
                })

    if uploaded_documents:
        st.success(
            f"{len(uploaded_documents)} uploaded document(s) "
            "read successfully."
        )

        for document in uploaded_documents:
            st.write(f"📄 {document['filename']}")

    if upload_errors:
        with st.expander("Uploaded files that could not be read"):
            for item in upload_errors:
                st.write(
                    f"**{item['filename']}** — {item['status']}"
                )


# --------------------------------------------------
# COMBINE AVAILABLE DOCUMENTS
# --------------------------------------------------

folder_documents = st.session_state.get(
    "loaded_documents", []
)

all_documents = folder_documents + uploaded_documents

st.divider()
st.subheader("Ask your documents")

if all_documents:
    st.caption(
        f"{len(all_documents)} document(s) available for questions."
    )
else:
    st.info(
        "Upload documents above, or add files to the "
        "application's documents folder."
    )

question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: Summarize the main concepts in my documents."
    ),
    height=100,
)

if st.button("Get Answer", type="primary"):
    if not all_documents:
        st.error("Please upload at least one readable document.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        combined_text = "\n\n".join(
            f"DOCUMENT: {document['filename']}\n"
            f"{document['text']}"
            for document in all_documents
        )

        with st.spinner("Groq AI is analyzing your documents..."):
            try:
                answer = answer_question(
                    combined_text,
                    question.strip(),
                )

                st.subheader("Answer")
                st.markdown(answer)

            except Exception as error:
                st.error(
                    "Unable to generate an answer. "
                    "Check your Groq API configuration and "
                    "try again."
                )
                st.caption(
                    f"Error type: {type(error).__name__}"
                )

st.caption(
    "Uploaded documents are processed for the current app session. "
    "This interface does not intentionally save uploaded files "
    "to the application's documents folder."
)
