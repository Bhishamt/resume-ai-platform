import re


class SectionDetector:
    # Predefined header patterns (case-insensitive regex)
    SECTION_PATTERNS = {
        "Summary": [
            r"\bsummary\b",
            r"\bprofessional summary\b",
            r"\bprofile\b",
            r"\babout me\b",
            r"\bobjective\b",
            r"\bcareer objective\b",
            r"\bprofessional profile\b",
        ],
        "Skills": [
            r"\bskills\b",
            r"\btechnical skills\b",
            r"\bcore competencies\b",
            r"\bkey skills\b",
            r"\bexpertise\b",
            r"\btechnologies\b",
            r"\bskills & technologies\b",
            r"\bskills and technologies\b",
        ],
        "Experience": [
            r"\bexperience\b",
            r"\bwork experience\b",
            r"\bprofessional experience\b",
            r"\bemployment history\b",
            r"\bwork history\b",
            r"\bcareer history\b",
            r"\bprofessional background\b",
        ],
        "Education": [
            r"\beducation\b",
            r"\bacademic background\b",
            r"\bacademic profile\b",
            r"\bacademic history\b",
            r"\bcredentials\b",
        ],
        "Projects": [
            r"\bprojects\b",
            r"\bpersonal projects\b",
            r"\bacademic projects\b",
            r"\bkey projects\b",
            r"\brecent projects\b",
            r"\bportfolio\b",
        ],
        "Certifications": [
            r"\bcertifications\b",
            r"\blicenses\b",
            r"\bcertificates\b",
            r"\bcourses\b",
            r"\blicenses & certifications\b",
            r"\blicenses and certifications\b",
        ],
    }

    @classmethod
    def detect_sections(cls, text: str) -> dict:
        """Scan the text for each resume section.

        Returns:
            dict containing:
                - detected_sections: list of section names found
                - missing_sections: list of section names not found
                - score: section presence score out of 100
        """
        if not text:
            return {
                "detected_sections": [],
                "missing_sections": list(cls.SECTION_PATTERNS.keys()),
                "score": 0,
            }

        detected = []
        missing = []

        # Split text into lines to perform line-level checks
        lines = [line.strip().lower() for line in text.split("\n") if line.strip()]

        for section, patterns in cls.SECTION_PATTERNS.items():
            found = False
            for pattern in patterns:
                # Compile pattern with word boundaries
                regex = re.compile(pattern, re.IGNORECASE)

                # Heuristic 1: Check if any line matches the section header exactly (or closely)
                for line in lines:
                    # Clean up common characters like numbers or bullets
                    clean_line = re.sub(r"^[\d\.\-\*•●○▪■]+", "", line).strip()
                    # Also strip colons at the end of headers
                    clean_line = clean_line.rstrip(":")
                    if len(clean_line) < 30 and regex.search(clean_line):
                        found = True
                        break

                if found:
                    break

                # Heuristic 2: Check general text presence as a fallback (word boundary search)
                if regex.search(text):
                    found = True
                    break

            if found:
                detected.append(section)
            else:
                missing.append(section)

        # Calculate rule-based explainable score
        reasons = []
        weighted_score = 10

        # Core sections (2 points each deduction if missing)
        core_sections = ["Summary", "Skills", "Experience", "Education", "Projects"]
        for sec in core_sections:
            if sec in missing:
                reasons.append({"rule": f"Missing {sec} section", "points": -2})
                weighted_score -= 2

        if "Certifications" in missing:
            reasons.append({"rule": "Missing Certifications section", "points": -1})
            weighted_score -= 1

        weighted_score = max(0, weighted_score)
        # Keep score out of 100 for backward compatibility
        score = int(round(weighted_score / 0.1))

        return {
            "detected_sections": detected,
            "missing_sections": missing,
            "score": score,
            "weighted_score": weighted_score,
            "reasons": reasons,
        }
