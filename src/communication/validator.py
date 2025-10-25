"""
Validation for LLM responses (messages and decisions).
"""

import json
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    error_message: Optional[str] = None
    parsed_data: Optional[dict] = None


class ResponseValidator:
    """Validates LLM responses for messages and decisions."""
    
    def __init__(self, config: dict):
        """
        Initialize validator with configuration.
        
        Args:
            config: Validation configuration dict
        """
        self.max_message_chars = config.get('max_message_chars', 200)
        self.max_reasoning_chars = config.get('max_reasoning_chars', 500)
        self.valid_actions = config.get('decision_validation', {}).get('valid_actions', ['Cooperate', 'Defect'])
        self.message_required_keys = config.get('message_validation', {}).get('required_keys', ['message'])
        self.decision_required_keys = config.get('decision_validation', {}).get('required_keys', ['reasoning', 'action'])
        self.check_empty = config.get('message_validation', {}).get('check_empty', True)
        self.check_empty_reasoning = config.get('decision_validation', {}).get('check_empty_reasoning', True)
    
    def validate_message(self, response: str) -> ValidationResult:
        """
        Validate a communication message response.
        
        Args:
            response: Raw response string from LLM
        
        Returns:
            ValidationResult with validation status and parsed data
        """
        # Try to parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON format: {str(e)}"
            )
        
        # Check if it's a dict
        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                error_message="Response must be a JSON object"
            )
        
        # Check required keys
        for key in self.message_required_keys:
            if key not in data:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Missing required key: '{key}'"
                )
        
        message = data.get('message', '')
        
        # Check if message is a string
        if not isinstance(message, str):
            return ValidationResult(
                is_valid=False,
                error_message="Message must be a string"
            )
        
        # Check if empty (if configured to check)
        if self.check_empty and not message.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Message cannot be empty"
            )
        
        # Check character limit
        if len(message) > self.max_message_chars:
            return ValidationResult(
                is_valid=False,
                error_message=f"Message exceeds maximum length of {self.max_message_chars} characters (got {len(message)})"
            )
        
        # Check encoding (UTF-8)
        try:
            message.encode('utf-8')
        except UnicodeEncodeError:
            return ValidationResult(
                is_valid=False,
                error_message="Message contains invalid UTF-8 characters"
            )
        
        return ValidationResult(
            is_valid=True,
            parsed_data=data
        )
    
    def validate_decision(self, response: str) -> ValidationResult:
        """
        Validate a decision response (reasoning + action).
        
        Args:
            response: Raw response string from LLM
        
        Returns:
            ValidationResult with validation status and parsed data
        """
        # Try to parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON format: {str(e)}"
            )
        
        # Check if it's a dict
        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                error_message="Response must be a JSON object"
            )
        
        # Check required keys
        for key in self.decision_required_keys:
            if key not in data:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Missing required key: '{key}'"
                )
        
        reasoning = data.get('reasoning', '')
        action = data.get('action', '')
        
        # Validate reasoning
        if not isinstance(reasoning, str):
            return ValidationResult(
                is_valid=False,
                error_message="Reasoning must be a string"
            )
        
        if self.check_empty_reasoning and not reasoning.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Reasoning cannot be empty"
            )
        
        if len(reasoning) > self.max_reasoning_chars:
            return ValidationResult(
                is_valid=False,
                error_message=f"Reasoning exceeds maximum length of {self.max_reasoning_chars} characters (got {len(reasoning)})"
            )
        
        # Validate action
        if not isinstance(action, str):
            return ValidationResult(
                is_valid=False,
                error_message="Action must be a string"
            )
        
        if action not in self.valid_actions:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid action: '{action}'. Must be one of {self.valid_actions}"
            )
        
        # Check encoding (UTF-8)
        try:
            reasoning.encode('utf-8')
        except UnicodeEncodeError:
            return ValidationResult(
                is_valid=False,
                error_message="Reasoning contains invalid UTF-8 characters"
            )
        
        return ValidationResult(
            is_valid=True,
            parsed_data=data
        )
    
    def validate_with_retry(self, response: str, validation_type: str, max_retries: int = 1) -> Tuple[ValidationResult, int]:
        """
        Validate response with retry logic (for future use with LLM retries).
        
        Args:
            response: Raw response string
            validation_type: 'message' or 'decision'
            max_retries: Maximum number of retries
        
        Returns:
            Tuple of (ValidationResult, attempts_used)
        """
        if validation_type == 'message':
            validate_func = self.validate_message
        elif validation_type == 'decision':
            validate_func = self.validate_decision
        else:
            raise ValueError(f"Invalid validation type: {validation_type}")
        
        result = validate_func(response)
        return result, 1  # For now, just return the result with 1 attempt
