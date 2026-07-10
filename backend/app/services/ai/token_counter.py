def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a string.
    Uses the common approximation of ~1.33 tokens per word for English text.
    """
    if not text:
        return 0
    words = text.split()
    return int(len(words) * 1.33)
