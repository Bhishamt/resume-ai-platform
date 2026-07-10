import re
import math
from typing import List, Dict

class SimilarityEngine:
    # Standard English stop words
    STOP_WORDS = {
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
        'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
        'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
        'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her', 'here', 'heres',
        'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in', 'into',
        'is', 'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my', 'myself', 'no', 'nor', 'not',
        'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
        'same', 'shant', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that',
        'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'theres', 'these', 'they', 'theyd',
        'theyll', 'theyre', 'theyve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
        'wasnt', 'we', 'wed', 'well', 'were', 'weve', 'werent', 'what', 'whats', 'when', 'whens', 'where', 'wheres',
        'which', 'while', 'who', 'whos', 'whom', 'why', 'whys', 'with', 'wont', 'would', 'wouldnt', 'you', 'youd',
        'youll', 'youre', 'youve', 'your', 'yours', 'yourself', 'yourselves'
    }

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        """Convert text to lowercase, split by words, and remove stopwords."""
        if not text:
            return []
        words = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
        return [w for w in words if w not in cls.STOP_WORDS]

    @classmethod
    def calculate_similarity(cls, doc1: str, doc2: str) -> float:
        """Compute the cosine similarity between doc1 and doc2 using TF-IDF vectors."""
        tokens1 = cls._tokenize(doc1)
        tokens2 = cls._tokenize(doc2)

        if not tokens1 or not tokens2:
            return 0.0

        # Term frequency for each document
        tf1: Dict[str, int] = {}
        for t in tokens1:
            tf1[t] = tf1.get(t, 0) + 1

        tf2: Dict[str, int] = {}
        for t in tokens2:
            tf2[t] = tf2.get(t, 0) + 1

        # Vocabulary is the union of words in both documents
        vocab = set(tf1.keys()).union(set(tf2.keys()))

        # IDF calculated locally for N=2
        idf: Dict[str, float] = {}
        for t in vocab:
            df = 0
            if t in tf1:
                df += 1
            if t in tf2:
                df += 1
            idf[t] = math.log(1.0 + (2.0 / df))

        # TF-IDF vectors
        vector1 = {t: (tf1[t] * idf[t]) for t in tf1}
        vector2 = {t: (tf2[t] * idf[t]) for t in tf2}

        # Cosine similarity calculation: dot_product / (norm1 * norm2)
        dot_product = 0.0
        for t in vector1:
            if t in vector2:
                dot_product += vector1[t] * vector2[t]

        norm1 = math.sqrt(sum(v ** 2 for v in vector1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vector2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return dot_product / (norm1 * norm2)
