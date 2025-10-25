"""
OpenAI LLM interface implementation.
"""

import os
from typing import Optional
from openai import OpenAI
from .base import BaseLLM


class OpenAIModel(BaseLLM):
    """OpenAI GPT model interface."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, 
                 max_tokens: int = 1000, api_key: Optional[str] = None):
        """
        Initialize OpenAI model.
        
        Args:
            model_name: OpenAI model identifier (e.g., 'gpt-3.5-turbo')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
        """
        super().__init__(model_name, temperature, max_tokens)
        
        # Get API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY env var not set")
        
        # Initialize client
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using OpenAI API.
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system instruction
        
        Returns:
            Raw text response from the model
        
        Raises:
            Exception: If API call fails
        """
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def get_token_count_estimate(self, text: str) -> int:
        """
        Rough estimate of token count (for cost tracking).
        ~4 chars per token is a rough approximation.
        
        Args:
            text: Text to estimate tokens for
        
        Returns:
            Estimated token count
        """
        return len(text) // 4
