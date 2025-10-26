"""
Google Gemini LLM interface implementation.
"""

import os
from typing import Optional
import google.generativeai as genai
from .base import BaseLLM

import logging

# Suppress the "ALTS creds ignored" warning
# This logger comes from the 'google-auth' library
logging.getLogger('google.auth.transport.grpc').setLevel(logging.ERROR)

# Suppress the "All log messages before absl::InitializeLog" warning
# This logger comes from the 'absl' library, a gRPC dependency
logging.getLogger('absl').setLevel(logging.ERROR)

class GeminiModel(BaseLLM):
    """Google Gemini model interface."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.7,
                 max_tokens: int = 1000, api_key: Optional[str] = None):
        """
        Initialize Gemini model.
        
        Args:
            model_name: Gemini model identifier (e.g., 'gemini-2.0-flash-exp')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response (max_output_tokens)
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
        """
        super().__init__(model_name, temperature, max_tokens)
        
        # Get API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided and GEMINI_API_KEY env var not set")
        
        # Configure and initialize model
        genai.configure(api_key=self.api_key)
        
        # Generation config
        self.generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using Gemini API.
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system instruction (prepended to prompt)
        
        Returns:
            Raw text response from the model
        
        Raises:
            Exception: If API call fails
        """
        try:
            # Gemini doesn't have separate system messages in the same way
            # We prepend system prompt to user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
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
