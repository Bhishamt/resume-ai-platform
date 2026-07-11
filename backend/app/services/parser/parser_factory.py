import os

from app.core.exceptions import BadRequestError
from app.services.parser.base_parser import BaseParser
from app.services.parser.docx_parser import DOCXParser
from app.services.parser.pdf_parser import PDFParser


class ParserFactory:
    """Factory class to retrieve the appropriate parser based on file characteristics."""

    @staticmethod
    def get_parser(filename: str, mime_type: str | None = None) -> BaseParser:
        """Return the parser corresponding to file extension or MIME type."""
        ext = os.path.splitext(filename)[1].lower()

        # Check by extension
        if ext == ".pdf" or mime_type == "application/pdf":
            return PDFParser()
        elif ext in [".docx", ".doc"] or mime_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            return DOCXParser()

        raise BadRequestError(
            f"Unsupported file format: {ext or mime_type}. Only PDF and DOCX are allowed."
        )
