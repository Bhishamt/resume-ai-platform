import re

class FormattingChecker:
    @classmethod
    def check_formatting(cls, text: str, detected_sections: list) -> dict:
        """Evaluate resume formatting parameters.
        
        Returns:
            dict containing:
                - details: dict of specific check results (boolean or value)
                - score: formatting score (0-100)
                - feedback: list of formatting recommendations
        """
        if not text:
            return {
                "details": {
                    "word_count": 0,
                    "has_name": False,
                    "has_email": False,
                    "has_phone": False,
                    "bullet_count": 0,
                    "section_count": 0
                },
                "score": 0,
                "feedback": ["Resume text is empty."]
            }

        feedback = []
        details = {}

        # 1. Word Count Check
        words = text.split()
        word_count = len(words)
        details["word_count"] = word_count
        length_score = 0
        if 300 <= word_count <= 1500:
            length_score = 20
        elif 150 <= word_count < 300 or 1500 < word_count <= 2000:
            length_score = 10
            feedback.append("Resume word count is slightly outside the optimal 300-1500 range.")
        else:
            length_score = 0
            feedback.append("Resume word count is either too short or too long. Aim for 300-1500 words.")

        # 2. Section Headings Check
        section_count = len(detected_sections)
        details["section_count"] = section_count
        headings_score = 0
        if section_count >= 4:
            headings_score = 10
        elif 1 <= section_count < 4:
            headings_score = 5
            feedback.append("Resume does not have enough clearly defined sections. Include Skills, Experience, Education, and Projects.")
        else:
            headings_score = 0
            feedback.append("No standard section headers detected. Check your resume's heading formatting.")

        # 3. Bullet Point Usage
        # Count common bullet characters or line starts like -, *, •, ●, ○, ▪, ■
        bullet_pattern = r"(?:^|\n)\s*[\-\*•●○▪■○]\s"
        # Also check for numbered bullets e.g., 1. 2.
        numbered_pattern = r"(?:^|\n)\s*\d+\.\s"
        
        bullets = re.findall(bullet_pattern, text)
        numbered = re.findall(numbered_pattern, text)
        bullet_count = len(bullets) + len(numbered)
        details["bullet_count"] = bullet_count
        
        bullet_score = 0
        if bullet_count >= 8:
            bullet_score = 20
        elif 3 <= bullet_count < 8:
            bullet_score = 10
            feedback.append("Increase bullet point usage to make achievements easier to read.")
        else:
            bullet_score = 0
            feedback.append("No bullet points detected. Structure your experience and projects with bulleted lists.")

        # 4. Contact Information
        # Name detection heuristic
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        has_name = False
        if lines:
            for line in lines[:3]:
                if any(kw in line.lower() for kw in ["resume", "cv", "curriculum", "email", "phone"]):
                    continue
                words_in_line = line.split()
                if 1 <= len(words_in_line) <= 4 and all(w[0].isupper() for w in words_in_line if w.isalpha()):
                    has_name = True
                    break
            if not has_name:
                # Fallback: check first line length
                has_name = len(lines[0]) < 40
        details["has_name"] = has_name
        name_score = 10 if has_name else 0
        if not has_name:
            feedback.append("Candidate name could not be identified at the top of the resume.")

        # Email detection
        email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
        email_match = re.search(email_pattern, text)
        has_email = email_match is not None
        details["has_email"] = has_email
        email_score = 20 if has_email else 0
        if not has_email:
            feedback.append("No email address detected. Ensure your email is clearly visible.")

        # Phone detection
        phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        phone_match = re.search(phone_pattern, text)
        has_phone = phone_match is not None
        details["has_phone"] = has_phone
        phone_score = 20 if has_phone else 0
        if not has_phone:
            feedback.append("No contact phone number detected.")

        # Calculate final formatting score
        total_score = length_score + headings_score + bullet_score + name_score + email_score + phone_score

        return {
            "details": details,
            "score": total_score,
            "feedback": feedback
        }
