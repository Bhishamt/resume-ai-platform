import time
import hashlib
from typing import Dict, Any, Optional

class AICache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def _get_key(self, prompt: str, provider: str, prompt_type: str) -> str:
        # Create a unique SHA256 key for cache lookup
        combined = f"{provider}:{prompt_type}:{prompt}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def get(self, prompt: str, provider: str, prompt_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached response if it exists and is not expired."""
        key = self._get_key(prompt, provider, prompt_type)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["data"]
            else:
                # Expired - remove from cache
                del self.cache[key]
        return None

    def set(self, prompt: str, provider: str, prompt_type: str, data: Dict[str, Any]):
        """Save a response in the cache with the current timestamp."""
        key = self._get_key(prompt, provider, prompt_type)
        self.cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    def clear(self):
        """Clear all cached responses."""
        self.cache.clear()

# Singleton cache instance
ai_cache = AICache()
