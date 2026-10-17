**# Smart Documentation Q\&A Agent**



**## 1. Project Overview**



**The Smart Documentation Q\&A Agent is a Python-based application that helps users find information from documents by entering questions. It extracts text from supported document formats and provides relevant sections from the selected document. It also includes an AI-powered answer mode using CrewAI and Google's Gemini API.**



**## 2. Objectives**



**- Extract text from PDF documents.**

**- Read DOCX, XLSX, and supported image files.**

**- Use OCR to extract text from scanned images.**

**- Find relevant document sections using keyword-based local search.**

**- Provide an optional AI-powered question-answering feature.**

**- Display extracted document content through a simple web interface.**



**## 3. Technologies Used**



**- Python**

**- Streamlit**

**- CrewAI**

**- Google Gemini API**

**- PyMuPDF**

**- Tesseract OCR**

**- Pytesseract**

**- Pillow**

**- Python-docx**

**- Openpyxl**

**- Python-dotenv**



**## 4. Features**



**- Simple and interactive web interface.**

**- Document selection from the documents folder.**

**- Local document search that works without API access.**

**- Optional AI-generated answers through Gemini and CrewAI.**

**- PDF text extraction.**

**- OCR support for scanned images and supported document pages.**

**- Text preview for extracted document content.**



**## 5. Project Structure**



**```text**

**smart-documentation-qa/**

**├── app.py**

**├── agent.py**

**├── document\_reader.py**

**├── test\_gemini.py**

**├── requirements.txt**

**├── .env**

**├── .gitignore**

**└── documents/**

&#x20;   **└── Your documents**

**```**



**\*\*Note:\*\* The `.env` file contains the API key and must not be uploaded to GitHub.**



**## 6. Installation**



**1. Install Python 3.12 or a compatible version.**

**2. Install Tesseract OCR separately for OCR functionality.**

**3. Open a terminal in the project directory.**

**4. Create and activate a Python virtual environment.**

**5. Install the required packages:**



**```bash**

**pip install -r requirements.txt**

**```**



**6. Create a `.env` file and add your Gemini API key:**



**```text**

**GEMINI\_API\_KEY=your\_api\_key\_here**

**```**



**Replace the placeholder with your own API key. Do not share it publicly.**



**## 7. Running the Application**



**Start the application using:**



**```bash**

**streamlit run app.py**

**```**



**Open the local URL displayed in the terminal, usually `http://localhost:8501`.**



**Select a document, enter a question, and choose Local Search or AI Answer mode.**



**## 8. Working Methodology**



**1. The application reads documents from the documents folder.**

**2. The document reader extracts available text and uses OCR where configured.**

**3. The user selects a document and enters a question.**

**4. Local Search identifies relevant text sections based on keyword matching.**

**5. AI Answer mode sends the document context and question to the configured Gemini model through CrewAI.**

**6. The result is displayed in the Streamlit interface.**



**## 9. Limitations**



**- Local Search uses keyword matching and may miss relevant sections when different terminology is used.**

**- AI Answer mode requires a working Gemini API configuration and available API quota.**

**- OCR accuracy depends on image quality and document formatting.**

**- Supported file formats depend on the document reader implementation.**



**## 10. Future Enhancements**



**- Semantic search and vector database integration.**

**- Improved document chunking and retrieval.**

**- Support for more file formats.**

**- Conversation history and downloadable answers.**

**- More robust citations showing the source page for each answer.**



**## 11. Conclusion**



**The Smart Documentation Q\&A Agent demonstrates how document extraction, OCR, keyword-based retrieval, and AI integration can be combined in a web application to make document information easier to find and understand.**



