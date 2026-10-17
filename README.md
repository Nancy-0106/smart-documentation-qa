# Smart Documentation Q&A Agent

## Project Overview

The Smart Documentation Q&A Agent is a Python-based application that allows users to ask questions about documents stored in a designated folder. It extracts document content, retrieves relevant text, and uses Groq AI to generate answers grounded in the available content.

## Features

- **Automatic Document Scanning:** Scans the `documents` folder and its subfolders for supported files.
- **Document Text Extraction:** Extracts text from PDF, Word, Excel, PowerPoint, and text-based files.
- **Image OCR:** Uses Tesseract OCR to extract text from images and scanned PDF pages.
- **AI-Powered Question Answering:** Uses the Groq API to answer questions using retrieved document excerpts.
- **Keyword-Based Retrieval:** Ranks text chunks according to their relevance to a user's question.
- **Missing-Information Handling:** Instructs the AI to indicate when retrieved excerpts do not provide enough information.
- **Streamlit Interface:** Provides a browser-based interface for scanning documents and asking questions.

## Technologies Used

- Python
- Streamlit
- Groq API
- Tesseract OCR
- PyMuPDF
- python-docx
- openpyxl
- python-pptx
- Pillow
- pytesseract
- python-dotenv

## Project Workflow

1. The user places supported documents inside the `documents` folder.
2. The application scans the folder and its subfolders.
3. The document reader extracts text from supported files and uses OCR where required.
4. The retrieval component selects text chunks relevant to the user's question.
5. The selected excerpts are sent to Groq AI.
6. The application displays the generated answer in the Streamlit interface.

## Supported File Formats

- PDF
- DOCX
- XLSX
- PPTX
- TXT and supported text-based formats
- PNG, JPG, JPEG, BMP, TIFF, and WEBP images

## Prerequisites

- Python 3.12 or a compatible supported Python version
- A Groq API key
- Tesseract OCR installed on Windows or the relevant operating system

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Nancy-0106/smart-documentation-qa.git
cd smart-documentation-qa
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Install dependencies

On Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or publish your API key.

### 5. Install and configure Tesseract OCR

Install Tesseract OCR and ensure its executable path matches the configuration in `document_reader.py`.

The default Windows path used by this project is:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 6. Add documents

Place the documents you want to analyze inside the `documents` folder. Create the folder if it does not already exist.

### 7. Run the application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Security Considerations

- Keep API keys and credentials out of source code and version control.
- Do not publish confidential, personal, or financial documents.
- Review document content before sending it to an external AI API.
- AI-generated answers may be incomplete or inaccurate and should be verified against the original documents.

## Current Limitations

- Retrieval uses keyword-based matching rather than semantic embeddings.
- OCR accuracy depends on image quality, text size, and image clarity.
- The application runs locally unless separately deployed to a hosting platform.
- The AI can only answer reliably when relevant information is extracted and included in the retrieved excerpts.

## Future Enhancements

- Semantic search using text embeddings.
- Source filename and page-level citations.
- Improved OCR preprocessing.
- User authentication and access controls.
- Deployment to a suitable hosting platform.

## Repository

[Smart Documentation Q&A Agent on GitHub](https://github.com/Nancy-0106/smart-documentation-qa)
