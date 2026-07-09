import re

class KeywordAnalyzer:
    # Predefined keyword lists by category
    KEYWORDS_BY_CATEGORY = {
        "Technical Skills": [
            "python", "javascript", "react", "fastapi", "django", "flask", "node.js", "node",
            "express", "html", "css", "tailwind", "sql", "postgresql", "postgres", "mysql",
            "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure", "git", "github",
            "ci/cd", "java", "c++", "c#", "typescript", "graphql", "rest api", "api", "rust",
            "go", "tensorflow", "pytorch", "machine learning", "data analytics", "pandas",
            "numpy", "scikit-learn", "spark", "hadoop", "c", "ruby", "rails", "php"
        ],
        "Soft Skills": [
            "leadership", "communication", "teamwork", "problem solving", "analytical",
            "organization", "time management", "agile", "scrum", "collaboration",
            "adaptability", "creativity", "critical thinking", "negotiation",
            "interpersonal", "conflict resolution", "mentoring"
        ],
        "Action Verbs": [
            "led", "designed", "developed", "built", "implemented", "created", "architected",
            "managed", "optimized", "achieved", "delivered", "coordinated", "initiated",
            "improved", "automated", "streamlined", "spearheaded", "formulated", "executed",
            "oversaw", "enhanced", "expanded", "decreased", "reduced", "increased",
            "integrated", "authored", "accelerated", "facilitated", "negotiated"
        ],
        "Industry Keywords": [
            "software development", "cloud computing", "database management", "machine learning",
            "systems architecture", "devops", "product management", "microservices", "frontend",
            "backend", "fullstack", "quality assurance", "security", "sdlc", "scalability",
            "high availability", "database administration", "web services", "software engineering",
            "saas", "scrum master", "system integration"
        ]
    }

    # High-priority keywords that are highly recommended in tech resumes
    CRITICAL_KEYWORDS = [
        "python", "javascript", "react", "sql", "docker", "git", "aws", "agile", "api", "ci/cd"
    ]

    @classmethod
    def analyze_keywords(cls, text: str) -> dict:
        """Scan the text for predefined keywords.
        
        Returns:
            dict containing:
                - found_by_category: dict mapping category to list of found terms
                - missing_keywords: list of recommended keywords missing in text
                - category_scores: dict mapping category to score out of 100
                - score: overall keyword score (0-100)
        """
        if not text:
            return {
                "found_by_category": {cat: [] for cat in cls.KEYWORDS_BY_CATEGORY},
                "missing_keywords": cls.CRITICAL_KEYWORDS,
                "category_scores": {cat: 0 for cat in cls.KEYWORDS_BY_CATEGORY},
                "score": 0
            }

        text_lower = text.lower()
        found_by_category = {}
        category_scores = {}
        
        # 1. Scan keywords by category
        for category, terms in cls.KEYWORDS_BY_CATEGORY.items():
            found_terms = []
            for term in terms:
                # Use word boundary matching for safety
                # Special escape logic for characters like c++, c#, .js
                escaped_term = re.escape(term)
                # If term ends or starts with special characters, adjust word boundary pattern
                if term.endswith("++") or term.endswith("#"):
                    pattern = rf"\b{escaped_term}"
                elif term.startswith("."):
                    pattern = rf"{escaped_term}\b"
                else:
                    pattern = rf"\b{escaped_term}\b"
                
                if re.search(pattern, text_lower):
                    # Format word nicely
                    display_term = term.title() if len(term) > 3 else term.upper()
                    if term == "node.js":
                        display_term = "Node.js"
                    elif term == "ci/cd":
                        display_term = "CI/CD"
                    elif term == "rest api":
                        display_term = "REST API"
                    found_terms.append(display_term)
            
            found_by_category[category] = sorted(list(set(found_terms)))

        # 2. Calculate category scores based on count thresholds
        # Technical: target 10 skills. Score = (count / 10) * 100, max 100.
        tech_count = len(found_by_category["Technical Skills"])
        category_scores["Technical Skills"] = min(100, int((tech_count / 10) * 100))

        # Soft Skills: target 5 skills. Score = (count / 5) * 100, max 100.
        soft_count = len(found_by_category["Soft Skills"])
        category_scores["Soft Skills"] = min(100, int((soft_count / 5) * 100))

        # Action Verbs: target 8 verbs. Score = (count / 8) * 100, max 100.
        verbs_count = len(found_by_category["Action Verbs"])
        category_scores["Action Verbs"] = min(100, int((verbs_count / 8) * 100))

        # Industry Keywords: target 5 keywords. Score = (count / 5) * 100, max 100.
        ind_count = len(found_by_category["Industry Keywords"])
        category_scores["Industry Keywords"] = min(100, int((ind_count / 5) * 100))

        # 3. Calculate Overall Keyword Score using category weights
        # Tech: 40%, Soft: 20%, Verbs: 20%, Industry: 20%
        overall_score = int(
            (category_scores["Technical Skills"] * 0.40) +
            (category_scores["Soft Skills"] * 0.20) +
            (category_scores["Action Verbs"] * 0.20) +
            (category_scores["Industry Keywords"] * 0.20)
        )

        # 4. Identify missing critical keywords
        missing_critical = []
        for kw in cls.CRITICAL_KEYWORDS:
            # Check if critical keyword was found in any category (case-insensitive check)
            kw_found = False
            for cat_list in found_by_category.values():
                if any(x.lower() == kw.lower() for x in cat_list):
                    kw_found = True
                    break
            if not kw_found:
                display_kw = kw.title() if len(kw) > 3 else kw.upper()
                if kw == "ci/cd":
                    display_kw = "CI/CD"
                missing_critical.append(display_kw)

        return {
            "found_by_category": found_by_category,
            "missing_keywords": missing_critical,
            "category_scores": category_scores,
            "score": overall_score
        }
