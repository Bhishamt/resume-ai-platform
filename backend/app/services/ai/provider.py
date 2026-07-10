from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: str = None, 
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response from the AI provider.

        Args:
            prompt: The main user prompt.
            system_prompt: Optional instructions for the model's behavior.
            json_mode: Whether to enforce JSON output formatting.

        Returns:
            Dict containing:
                "response": str (the generated text/JSON response)
                "tokens": Dict with prompt_tokens, completion_tokens, total_tokens
                "response_time": float (duration of the API call in seconds)
        """
        pass
