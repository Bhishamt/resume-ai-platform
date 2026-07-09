import fitz  # PyMuPDF
from app.services.parser.base_parser import BaseParser, ParsedResumeData

class PDFParser(BaseParser):
    """Resume parser implementation for PDF documents."""

    def parse(self, file_path: str) -> ParsedResumeData:
        """Extract text from PDF pages and return parsed metadata."""
        raw_text = ""
        try:
            # Open PDF file
            with fitz.open(file_path) as doc:
                for page in doc:
                    raw_text += page.get_text()
        except Exception as e:
            # Fallback/Empty text if parsing fails
            raw_text = ""

        # Extract contact information and sections using base helper
        extracted = self.extract_metadata(raw_text)

        return ParsedResumeData(
            name=extracted["name"],
            email=extracted["email"],
            phone=extracted["phone"],
            skills=extracted["skills"],
            education=extracted["education"],
            experience=extracted["experience"],
            projects=extracted["projects"],
            certifications=extracted["certifications"],
            raw_text=raw_text,
        )
