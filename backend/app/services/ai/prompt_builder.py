from typing import Dict, Any
from app.services.ai.prompt_templates import PromptTemplate

class PromptBuilder:
    @staticmethod
    def build(template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """
        Merge template with variables safely.
        Ensure all required variables are present. If variables are missing, raise ValueError.
        """
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables for prompt '{template.name}': {missing_vars}")

        # Clean variables (convert None or empty to empty string/lists)
        formatted_vars = {}
        for var in template.variables:
            val = variables.get(var)
            if val is None:
                formatted_vars[var] = ""
            elif isinstance(val, (list, tuple)):
                formatted_vars[var] = ", ".join(str(item) for item in val)
            else:
                formatted_vars[var] = str(val)

        try:
            return template.template.format(**formatted_vars)
        except Exception as e:
            raise ValueError(f"Failed to build prompt '{template.name}': {str(e)}") from e
