import abc
import re
from typing import TypedDict


class ParsedResumeData(TypedDict):
    name: str | None
    email: str | None
    phone: str | None
    skills: list[str]
    education: list[str]
    experience: list[str]
    projects: list[str]
    certifications: list[str]
    raw_text: str


class BaseParser(abc.ABC):
    """Abstract base class defining the Resume Parser interface."""

    @abc.abstractmethod
    def parse(self, file_path: str) -> ParsedResumeData:
        """Parse text from file and extract structured information."""
        pass

    def extract_metadata(self, text: str) -> dict:
        """Heuristic-based extraction of name, email, phone, and section fields."""
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        name = self._extract_name(text)

        skills = self._extract_section_keywords(text, "skills")
        education = self._extract_section_keywords(text, "education")
        experience = self._extract_section_keywords(text, "experience")
        projects = self._extract_section_keywords(text, "projects")
        certifications = self._extract_section_keywords(text, "certifications")

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
        }

    def _extract_email(self, text: str) -> str | None:
        """Extract email using a standard regex pattern."""
        pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> str | None:
        """Extract phone numbers using standard regex heuristics."""
        pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_name(self, text: str) -> str | None:
        """Extract name (heuristic: first non-empty lines, looking for capitalized words)."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return None

        # Check the first few lines for typical Name pattern: 2-3 capitalized words
        for line in lines[:3]:
            # Skip lines containing common headers or emails/phones
            if any(
                kw in line.lower()
                for kw in ["resume", "cv", "curriculum", "email", "phone", "address"]
            ):
                continue
            if "@" in line or any(c.isdigit() for c in line if c in "+-() "):
                # Skip if it looks like email or phone
                if len([c for c in line if c.isdigit()]) > 5:
                    continue
            words = line.split()
            if 1 <= len(words) <= 4 and all(
                w[0].isupper() for w in words if w.isalpha()
            ):
                return line

        return lines[0] if lines else None

    def _extract_section_keywords(self, text: str, section_type: str) -> list[str]:
        """Heuristic check to parse section items using a predefined list of industry terms."""
        text_lower = text.lower()
        found = []

        keywords_map = {
            "skills": [
                "python",
                "javascript",
                "react",
                "fastapi",
                "django",
                "flask",
                "node.js",
                "html",
                "css",
                "tailwind",
                "sql",
                "postgresql",
                "mysql",
                "mongodb",
                "redis",
                "docker",
                "kubernetes",
                "aws",
                "gcp",
                "azure",
                "git",
                "github",
                "ci/cd",
                "java",
                "c++",
                "c#",
                "typescript",
                "graphql",
                "rest api",
                "rust",
                "go",
                "agile",
                "scrum",
                "machine learning",
                "data analytics",
                "tensorflow",
                "pytorch",
            ],
            "education": [
                "bachelor",
                "master",
                "phd",
                "b.sc",
                "b.s",
                "m.sc",
                "m.s",
                "b.tech",
                "m.tech",
                "university",
                "college",
                "degree",
                "diploma",
                "gpa",
                "major",
                "computer science",
                "engineering",
                "mathematics",
                "physics",
            ],
            "experience": [
                "experience",
                "work history",
                "employment",
                "intern",
                "developer",
                "engineer",
                "architect",
                "lead",
                "manager",
                "director",
                "consultant",
                "analyst",
                "years",
                "months",
                "responsibilities",
                "accomplishments",
            ],
            "projects": [
                "project",
                "portfolio",
                "personal project",
                "academic project",
                "github repository",
                "designed",
                "developed",
                "built",
                "implemented",
                "created",
                "architected",
            ],
            "certifications": [
                "certification",
                "certified",
                "aws certified",
                "pmp",
                "scrum master",
                "comptia",
                "cisco",
                "ccna",
                "gcp certified",
                "udemy",
                "coursera",
                "licence",
            ],
        }

        # For skills, scan directly for keywords present in the text
        if section_type == "skills":
            for skill in keywords_map["skills"]:
                # Match skill as a whole word boundary
                pattern = rf"\b{re.escape(skill)}\b"
                if re.search(pattern, text_lower):
                    found.append(skill.title() if len(skill) > 3 else skill.upper())
            return sorted(list(set(found)))

        # For other sections, look for header presence and extract surrounding sentences or list matching keywords
        section_keywords = keywords_map.get(section_type, [])
        for kw in section_keywords:
            if kw in text_lower:
                found.append(kw)

        return sorted(list(set(found)))
