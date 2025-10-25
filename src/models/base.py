"""
Base class for LLM interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json


class BaseLLM(ABC):
    """Abstract base class for LLM interfaces."""
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 1000):
        """
        Initialize LLM interface.
        
        Args:
            model_name: Name/identifier of the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system instruction
        
        Returns:
            Raw text response from the model
        
        Raises:
            Exception: If API call fails
        """
        pass
    
    def generate_message(self, context: Dict[str, Any], prompt_template: str) -> str:
        """
        Generate a communication message.
        
        Args:
            context: Context dictionary with game state/history
            prompt_template: Template string for the prompt
        
        Returns:
            Raw JSON response string
        """
        formatted_prompt = self._format_prompt(prompt_template, context)
        return self.generate_response(formatted_prompt)
    
    def generate_decision(self, context: Dict[str, Any], prompt_template: str) -> str:
        """
        Generate a decision (reasoning + action).
        
        Args:
            context: Context dictionary with game state/history
            prompt_template: Template string for the prompt
        
        Returns:
            Raw JSON response string
        """
        formatted_prompt = self._format_prompt(prompt_template, context)
        return self.generate_response(formatted_prompt)
    
    def _format_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """
        Format prompt template with context values.
        
        Args:
            template: Prompt template with placeholders
            context: Context dictionary
        
        Returns:
            Formatted prompt string
        """
        # Simple formatting - can be enhanced later
        try:
            return template.format(**context)
        except KeyError as e:
            # If direct formatting fails, just return template
            # More sophisticated formatting can be added later
            return template
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name}, temp={self.temperature})"
