import fitz

def process_pdf(file_bytes: bytes) -> str:
    """
    Parses a PDF file from bytes and extracts its text content.

    Args:
        file_bytes: The content of the PDF file as bytes.

    Returns:
        The extracted text as a single string.
    """
    try:
        # Open the PDF from the byte stream
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

        full_text = []
        # Iterate through each page of the document
        for page in pdf_document:
            full_text.append(page.get_text("text"))

        pdf_document.close()

        return "\n".join(full_text)
    except Exception as e:
        # If any error occurs during parsing, we raise an exception
        # that the API layer can catch and handle.
        print(f"An error occurred during PDF parsing: {e}")
        raise ValueError("Failed to parse the provided PDF file.")



