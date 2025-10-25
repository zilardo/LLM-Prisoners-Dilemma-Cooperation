"""
Test script for response validator.
Run this to verify validation logic works correctly.
"""

import sys
sys.path.append('src')

from communication.validator import ResponseValidator, ValidationResult


# Test configuration
TEST_CONFIG = {
    'max_message_chars': 200,
    'max_reasoning_chars': 500,
    'message_validation': {
        'required_keys': ['message'],
        'check_empty': True,
        'check_encoding': True
    },
    'decision_validation': {
        'required_keys': ['reasoning', 'action'],
        'valid_actions': ['Cooperate', 'Defect'],
        'check_empty_reasoning': True
    }
}


def test_valid_messages():
    """Test valid message responses."""
    print("=" * 50)
    print("Testing Valid Messages")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    test_cases = [
        ('{"message": "Hello, let\'s cooperate!"}', "Simple message"),
        ('{"message": "I think we should build trust by cooperating initially."}', "Longer message"),
        ('{"message": "A"}', "Single character"),
        ('{"message": "' + 'x' * 200 + '"}', "Max length (200 chars)"),
    ]
    
    for response, description in test_cases:
        result = validator.validate_message(response)
        status = "✅" if result.is_valid else "❌"
        print(f"{status} {description}: {result.is_valid}")
        if not result.is_valid:
            print(f"   Error: {result.error_message}")
        assert result.is_valid, f"Should be valid: {description}"
    
    print("\n✅ All valid message tests passed!\n")


def test_invalid_messages():
    """Test invalid message responses."""
    print("=" * 50)
    print("Testing Invalid Messages")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    test_cases = [
        ('not json at all', "Not JSON"),
        ('{"wrong_key": "value"}', "Missing 'message' key"),
        ('{"message": 123}', "Message not a string"),
        ('{"message": ""}', "Empty message"),
        ('{"message": "   "}', "Whitespace only message"),
        ('{"message": "' + 'x' * 201 + '"}', "Exceeds max length (201 chars)"),
        ('[]', "Array instead of object"),
        ('{message: "no quotes"}', "Invalid JSON syntax"),
    ]
    
    for response, description in test_cases:
        result = validator.validate_message(response)
        status = "✅" if not result.is_valid else "❌"
        print(f"{status} {description}: Invalid (expected)")
        if result.is_valid:
            print(f"   ERROR: Should have been invalid!")
        else:
            print(f"   Error caught: {result.error_message}")
        assert not result.is_valid, f"Should be invalid: {description}"
    
    print("\n✅ All invalid message tests passed!\n")


def test_valid_decisions():
    """Test valid decision responses."""
    print("=" * 50)
    print("Testing Valid Decisions")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    test_cases = [
        (
            '{"reasoning": "They cooperated last round, so I will too.", "action": "Cooperate"}',
            "Simple cooperate decision"
        ),
        (
            '{"reasoning": "They have defected twice in a row. I need to protect myself.", "action": "Defect"}',
            "Simple defect decision"
        ),
        (
            '{"reasoning": "' + 'x' * 500 + '", "action": "Cooperate"}',
            "Max reasoning length (500 chars)"
        ),
        (
            '{"reasoning": "Short", "action": "Defect"}',
            "Short reasoning"
        ),
    ]
    
    for response, description in test_cases:
        result = validator.validate_decision(response)
        status = "✅" if result.is_valid else "❌"
        print(f"{status} {description}: {result.is_valid}")
        if not result.is_valid:
            print(f"   Error: {result.error_message}")
        assert result.is_valid, f"Should be valid: {description}"
    
    print("\n✅ All valid decision tests passed!\n")


def test_invalid_decisions():
    """Test invalid decision responses."""
    print("=" * 50)
    print("Testing Invalid Decisions")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    test_cases = [
        ('not json', "Not JSON"),
        ('{"reasoning": "test"}', "Missing 'action' key"),
        ('{"action": "Cooperate"}', "Missing 'reasoning' key"),
        ('{"reasoning": "", "action": "Cooperate"}', "Empty reasoning"),
        ('{"reasoning": "   ", "action": "Cooperate"}', "Whitespace only reasoning"),
        ('{"reasoning": "test", "action": "Maybe"}', "Invalid action value"),
        ('{"reasoning": "test", "action": "cooperate"}', "Wrong case for action"),
        ('{"reasoning": 123, "action": "Cooperate"}', "Reasoning not a string"),
        ('{"reasoning": "test", "action": 123}', "Action not a string"),
        ('{"reasoning": "' + 'x' * 501 + '", "action": "Cooperate"}', "Reasoning too long (501 chars)"),
        ('[]', "Array instead of object"),
    ]
    
    for response, description in test_cases:
        result = validator.validate_decision(response)
        status = "✅" if not result.is_valid else "❌"
        print(f"{status} {description}: Invalid (expected)")
        if result.is_valid:
            print(f"   ERROR: Should have been invalid!")
        else:
            print(f"   Error caught: {result.error_message}")
        assert not result.is_valid, f"Should be invalid: {description}"
    
    print("\n✅ All invalid decision tests passed!\n")


def test_parsed_data():
    """Test that valid responses return parsed data."""
    print("=" * 50)
    print("Testing Parsed Data Extraction")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    # Test message parsing
    message_response = '{"message": "Let\'s cooperate!"}'
    result = validator.validate_message(message_response)
    assert result.is_valid
    assert result.parsed_data is not None
    assert result.parsed_data['message'] == "Let's cooperate!"
    print("✅ Message data parsed correctly")
    
    # Test decision parsing
    decision_response = '{"reasoning": "Build trust first", "action": "Cooperate"}'
    result = validator.validate_decision(decision_response)
    assert result.is_valid
    assert result.parsed_data is not None
    assert result.parsed_data['reasoning'] == "Build trust first"
    assert result.parsed_data['action'] == "Cooperate"
    print("✅ Decision data parsed correctly")
    
    print("\n✅ Parsed data tests passed!\n")


def test_edge_cases():
    """Test edge cases and special characters."""
    print("=" * 50)
    print("Testing Edge Cases")
    print("=" * 50)
    
    validator = ResponseValidator(TEST_CONFIG)
    
    # Test with special characters
    special_chars_message = '{"message": "Hello! 🤝 Let\'s work together. #cooperation"}'
    result = validator.validate_message(special_chars_message)
    print(f"✅ Special characters in message: {result.is_valid}")
    assert result.is_valid
    
    # Test with newlines
    newline_message = '{"message": "Line 1\\nLine 2"}'
    result = validator.validate_message(newline_message)
    print(f"✅ Newlines in message: {result.is_valid}")
    assert result.is_valid
    
    # Test with quotes
    quotes_message = '{"message": "They said \\"cooperate\\" so I will."}'
    result = validator.validate_message(quotes_message)
    print(f"✅ Escaped quotes in message: {result.is_valid}")
    assert result.is_valid
    
    # Test exact boundary (200 chars)
    exact_boundary = '{"message": "' + 'a' * 200 + '"}'
    result = validator.validate_message(exact_boundary)
    print(f"✅ Exact 200 char boundary: {result.is_valid}")
    assert result.is_valid
    
    # Test one over boundary (201 chars)
    over_boundary = '{"message": "' + 'a' * 201 + '"}'
    result = validator.validate_message(over_boundary)
    print(f"✅ 201 chars correctly rejected: {not result.is_valid}")
    assert not result.is_valid
    
    print("\n✅ Edge case tests passed!\n")


def test_custom_config():
    """Test validator with custom configuration."""
    print("=" * 50)
    print("Testing Custom Configuration")
    print("=" * 50)
    
    # Custom config with different limits
    custom_config = {
        'max_message_chars': 50,
        'max_reasoning_chars': 100,
        'message_validation': {
            'required_keys': ['message'],
            'check_empty': False  # Allow empty messages
        },
        'decision_validation': {
            'required_keys': ['reasoning', 'action'],
            'valid_actions': ['Yes', 'No'],  # Different actions
            'check_empty_reasoning': False
        }
    }
    
    validator = ResponseValidator(custom_config)
    
    # Test with custom limits
    message_51 = '{"message": "' + 'x' * 51 + '"}'
    result = validator.validate_message(message_51)
    print(f"✅ Custom 50 char limit enforced: {not result.is_valid}")
    assert not result.is_valid
    
    # Test with custom actions
    custom_action = '{"reasoning": "test", "action": "Yes"}'
    result = validator.validate_decision(custom_action)
    print(f"✅ Custom action 'Yes' accepted: {result.is_valid}")
    assert result.is_valid
    
    # Test old actions don't work
    old_action = '{"reasoning": "test", "action": "Cooperate"}'
    result = validator.validate_decision(old_action)
    print(f"✅ Old action 'Cooperate' rejected: {not result.is_valid}")
    assert not result.is_valid
    
    # Test empty message allowed
    empty_message = '{"message": ""}'
    result = validator.validate_message(empty_message)
    print(f"✅ Empty message allowed with config: {result.is_valid}")
    assert result.is_valid
    
    print("\n✅ Custom configuration tests passed!\n")


if __name__ == "__main__":
    test_valid_messages()
    test_invalid_messages()
    test_valid_decisions()
    test_invalid_decisions()
    test_parsed_data()
    test_edge_cases()
    test_custom_config()
    
    print("=" * 50)
    print("🎉 ALL VALIDATION TESTS PASSED!")
    print("=" * 50)
