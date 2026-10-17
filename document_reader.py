
import os
from pathlib import Path
from io import BytesIO

import pytesseract
from PIL import Image, ImageOps, ImageEnhance

import fitz
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation


# --------------------------------------------------
# TESSERACT OCR CONFIGURATION
# --------------------------------------------------

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# --------------------------------------------------
# SUPPORTED FILE TYPES
# --------------------------------------------------

TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".sql", ".log", ".json",
    ".xml", ".yaml", ".yml", ".ini", ".cfg", ".csv",
    ".html", ".htm", ".css", ".js", ".ts"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".bmp",
    ".tif", ".tiff", ".webp"
}

SUPPORTED_EXTENSIONS = (
    TEXT_EXTENSIONS
    | IMAGE_EXTENSIONS
    | {".pdf", ".docx", ".xlsx", ".pptx"}
)

MAX_FILE_SIZE = 30 * 1024 * 1024


# --------------------------------------------------
# IMAGE OCR
# --------------------------------------------------

def extract_image_text(image):
    """Extract text from a PIL image using Tesseract OCR."""
    try:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        # Improve contrast before OCR.
        image = ImageEnhance.Contrast(image).enhance(1.5)

        text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        return text.strip()

    except pytesseract.TesseractNotFoundError:
        return (
            "OCR ERROR: Tesseract executable was not found. "
            "Check TESSERACT_PATH in document_reader.py."
        )

    except Exception as error:
        return f"OCR ERROR: {type(error).__name__}: {error}"


def extract_image_file(path):
    """Read an image file and extract its text."""
    try:
        with Image.open(path) as image:
            return extract_image_text(image)

    except Exception as error:
        return f"IMAGE ERROR: {type(error).__name__}: {error}"


# --------------------------------------------------
# PDF READER
# --------------------------------------------------

def read_pdf(path):
    """Extract embedded text from PDFs and OCR scanned pages."""
    extracted = []

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            page_text = page.get_text("text").strip()

            if page_text:
                extracted.append(
                    f"[Source page: {page_number}]\n{page_text}"
                )
            else:
                # Render scanned pages as images for OCR.
                try:
                    pixmap = page.get_pixmap(
                        matrix=fitz.Matrix(2, 2),
                        alpha=False
                    )

                    image = Image.open(
                        BytesIO(pixmap.tobytes("png"))
                    )

                    ocr_text = extract_image_text(image)

                    if ocr_text:
                        extracted.append(
                            f"[Source page: {page_number} - OCR]\n"
                            f"{ocr_text}"
                        )

                except Exception as error:
                    extracted.append(
                        f"[Source page: {page_number}]\n"
                        f"Page extraction error: {type(error).__name__}"
                    )

    return "\n\n".join(extracted).strip()


# --------------------------------------------------
# WORD READER
# --------------------------------------------------

def read_docx(path):
    """Extract paragraphs and tables from a Word document."""
    document = Document(path)
    parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            parts.append(text)

    for table_number, table in enumerate(document.tables, start=1):
        parts.append(f"[Table {table_number}]")

        for row in table.rows:
            values = [
                cell.text.replace("\n", " ").strip()
                for cell in row.cells
            ]

            parts.append(" | ".join(values))

    return "\n".join(parts).strip()


# --------------------------------------------------
# EXCEL READER
# --------------------------------------------------

def read_xlsx(path):
    """Extract cell values from Excel worksheets."""
    workbook = load_workbook(
        path,
        read_only=True,
        data_only=True
    )

    parts = []

    try:
        for sheet in workbook.worksheets:
            parts.append(f"[Sheet: {sheet.title}]")

            for row in sheet.iter_rows(values_only=True):
                values = [
                    str(value) if value is not None else ""
                    for value in row
                ]

                if any(value.strip() for value in values):
                    parts.append(" | ".join(values))

    finally:
        workbook.close()

    return "\n".join(parts).strip()


# --------------------------------------------------
# POWERPOINT READER
# --------------------------------------------------

def read_pptx(path):
    """Extract text from PowerPoint slides."""
    presentation = Presentation(path)
    parts = []

    for slide_number, slide in enumerate(
        presentation.slides,
        start=1
    ):
        parts.append(f"[Slide {slide_number}]")

        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()

                if text:
                    parts.append(text)

            if shape.has_table:
                for row in shape.table.rows:
                    values = [
                        cell.text.strip()
                        for cell in row.cells
                    ]

                    parts.append(" | ".join(values))

    return "\n".join(parts).strip()


# --------------------------------------------------
# GENERAL DOCUMENT READER
# --------------------------------------------------

def read_document(path):
    """Read a supported document based on its extension."""
    path = Path(path)
    extension = path.suffix.lower()

    try:
        if not path.is_file():
            return ""

        if path.stat().st_size > MAX_FILE_SIZE:
            return (
                "ERROR: File exceeds the 30 MB size limit."
            )

        if extension == ".pdf":
            return read_pdf(str(path))

        if extension == ".docx":
            return read_docx(str(path))

        if extension == ".xlsx":
            return read_xlsx(str(path))

        if extension == ".pptx":
            return read_pptx(str(path))

        if extension in TEXT_EXTENSIONS:
            try:
                return path.read_text(
                    encoding="utf-8"
                ).strip()

            except UnicodeDecodeError:
                return path.read_text(
                    encoding="latin-1"
                ).strip()

        if extension in IMAGE_EXTENSIONS:
            return extract_image_file(str(path))

        return ""

    except Exception as error:
        return (
            f"ERROR: Could not read file. "
            f"{type(error).__name__}: {error}"
        )


# --------------------------------------------------
# READ A FILE UPLOADED TO STREAMLIT
# --------------------------------------------------

def read_uploaded_file(uploaded_file):
    """Read an uploaded Streamlit file object."""
    filename = getattr(
        uploaded_file,
        "name",
        "uploaded_file"
    )

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return ""

    try:
        file_bytes = uploaded_file.getvalue()

        if len(file_bytes) > MAX_FILE_SIZE:
            return "ERROR: File exceeds the 30 MB size limit."

        if extension in IMAGE_EXTENSIONS:
            with Image.open(BytesIO(file_bytes)) as image:
                return extract_image_text(image)

        if extension == ".pdf":
            extracted = []

            with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
                for page_number, page in enumerate(pdf, start=1):
                    page_text = page.get_text("text").strip()

                    if page_text:
                        extracted.append(
                            f"[Source page: {page_number}]\n{page_text}"
                        )
                    else:
                        pixmap = page.get_pixmap(
                            matrix=fitz.Matrix(2, 2),
                            alpha=False
                        )

                        image = Image.open(
                            BytesIO(pixmap.tobytes("png"))
                        )

                        text = extract_image_text(image)

                        if text:
                            extracted.append(
                                f"[Source page: {page_number} - OCR]\n{text}"
                            )

            return "\n\n".join(extracted).strip()

        # For other formats, save a temporary copy so
        # the same readers can process the file.
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / Path(filename).name
            temp_path.write_bytes(file_bytes)

            return read_document(temp_path)

    except Exception as error:
        return (
            f"ERROR: Could not read uploaded file. "
            f"{type(error).__name__}: {error}"
        )


# --------------------------------------------------
# COMBINE EXTRACTED DOCUMENT CONTENT
# --------------------------------------------------

def combine_document_text(documents):
    """Combine extracted text from a list of document results."""
    parts = []

    for document in documents:
        filename = document.get("filename", "Unknown document")
        text = document.get("text", "")

        if text and text.strip():
            parts.append(
                f"[Document: {filename}]\n{text}"
            )

    return "\n\n".join(parts)


# --------------------------------------------------
# SCAN THE DOCUMENTS FOLDER RECURSIVELY
# --------------------------------------------------

def read_folder_documents(folder_path):
    """
    Scan a folder and its subfolders for supported documents.

    Returns a list of dictionaries containing filename,
    text, and status.
    """
    folder = Path(folder_path)
    results = []

    if not folder.exists():
        return [{
            "filename": str(folder),
            "text": "",
            "status": "Folder does not exist."
        }]

    if not folder.is_dir():
        return [{
            "filename": str(folder),
            "text": "",
            "status": "Path is not a directory."
        }]

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue

        # Skip hidden files and temporary Office files.
        if any(part.startswith(".") for part in path.parts):
            continue

        if path.name.startswith("~$"):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative_name = str(path.relative_to(folder))

        if path.stat().st_size > MAX_FILE_SIZE:
            results.append({
                "filename": relative_name,
                "text": "",
                "status": "Skipped: file exceeds 30 MB."
            })
            continue

        text = read_document(path)

        if text.startswith("ERROR:") or text.startswith("OCR ERROR:"):
            status = text
            extracted_text = ""
        elif text.strip():
            status = "Read successfully"
            extracted_text = text
        else:
            status = "No text extracted"
            extracted_text = ""

        results.append({
            "filename": relative_name,
            "text": extracted_text,
            "status": status
        })

    return results
