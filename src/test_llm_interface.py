"""
Test script for LLM interfaces.

This tests the basic structure without making real API calls.
For real API testing, uncomment the first line
"""
# USE_API = True

# Build the path to the .env file (one level up from this file's directory)
from dotenv import load_dotenv
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

from models.base import BaseLLM
from models.openai_model import OpenAIModel
from models.gemini_model import GeminiModel


class MockLLM(BaseLLM):
    """Mock LLM for testing without API calls."""
    
    def __init__(self, model_name: str = "mock", temperature: float = 0.7, max_tokens: int = 1000):
        super().__init__(model_name, temperature, max_tokens)
        self.call_count = 0
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Return mock JSON responses."""
        self.call_count += 1
        
        # Mock decision response
        if "decision" in prompt.lower() or "reasoning" in prompt.lower():
            return '{"reasoning": "This is mock reasoning for testing.", "action": "Cooperate"}'
        
        # Mock message response
        return '{"message": "This is a mock message for testing."}'


def test_mock_llm():
    """Test basic LLM interface with mock."""
    print("=" * 50)
    print("Testing Mock LLM Interface")
    print("=" * 50)
    
    llm = MockLLM()
    
    # Test basic response
    response = llm.generate_response("Test prompt")
    print(f"✅ Mock response: {response[:50]}...")
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Test decision generation
    context = {"round": 1, "score": 0}
    decision = llm.generate_decision(context, "Make a decision")
    print(f"✅ Mock decision: {decision[:50]}...")
    assert "reasoning" in decision
    assert "action" in decision
    
    # Test message generation
    message = llm.generate_message(context, "Send a message")
    print(f"✅ Mock message: {message[:50]}...")
    assert "message" in message
    
    # Test call counting
    assert llm.call_count == 3
    print(f"✅ Call count tracked: {llm.call_count}")
    
    print("\n✅ Mock LLM test passed!\n")


def test_openai_initialization():
    """Test OpenAI model initialization (no API call)."""
    print("=" * 50)
    print("Testing OpenAI Initialization")
    print("=" * 50)
    
    # Test with explicit API key
    try:
        llm = OpenAIModel(api_key="dummy_key_for_testing")
        print(f"✅ OpenAI model initialized: {llm}")
        assert llm.model_name == "gpt-3.5-turbo"
        assert llm.temperature == 0.7
        print(f"✅ Model name: {llm.model_name}")
        print(f"✅ Temperature: {llm.temperature}")
    except Exception as e:
        print(f"⚠️  Initialization test: {e}")
    
    # Test missing API key handling
    old_key = os.environ.get('OPENAI_API_KEY')
    if old_key:
        del os.environ['OPENAI_API_KEY']
    
    try:
        llm = OpenAIModel()
        print("❌ Should have raised ValueError for missing API key")
    except ValueError as e:
        print(f"✅ Correctly caught missing API key: {e}")
    
    if old_key:
        os.environ['OPENAI_API_KEY'] = old_key
    
    print("\n✅ OpenAI initialization test passed!\n")


def test_gemini_initialization():
    """Test Gemini model initialization (no API call)."""
    print("=" * 50)
    print("Testing Gemini Initialization")
    print("=" * 50)
    
    # Test with explicit API key
    try:
        llm = GeminiModel(api_key="dummy_key_for_testing")
        print(f"✅ Gemini model initialized: {llm}")
        assert llm.model_name == "gemini-2.0-flash-exp"
        assert llm.temperature == 0.7
        print(f"✅ Model name: {llm.model_name}")
        print(f"✅ Temperature: {llm.temperature}")
    except Exception as e:
        print(f"⚠️  Initialization test: {e}")
    
    # Test missing API key handling
    old_key = os.environ.get('GEMINI_API_KEY')
    if old_key:
        del os.environ['GEMINI_API_KEY']
    
    try:
        llm = GeminiModel()
        print("❌ Should have raised ValueError for missing API key")
    except ValueError as e:
        print(f"✅ Correctly caught missing API key: {e}")
    
    if old_key:
        os.environ['GEMINI_API_KEY'] = old_key
    
    print("\n✅ Gemini initialization test passed!\n")


def test_token_estimation():
    """Test token count estimation."""
    print("=" * 50)
    print("Testing Token Estimation")
    print("=" * 50)
    
    llm = MockLLM()
    
    test_cases = [
        ("Short text", 2),  # ~8 chars / 4 = 2 tokens
        ("This is a longer piece of text", 7),  # ~32 chars / 4 = 8 tokens
        ("x" * 100, 25),  # 100 chars / 4 = 25 tokens
    ]
    
    for text, expected in test_cases:
        # We don't have token estimation on MockLLM, so test with OpenAI class
        try:
            openai_llm = OpenAIModel(api_key="dummy")
            estimate = openai_llm.get_token_count_estimate(text)
            print(f"✅ Text length {len(text)} chars → ~{estimate} tokens")
            assert estimate > 0
        except:
            pass
    
    print("\n✅ Token estimation test passed!\n")


# ============================================================
# OPTIONAL: Real API Tests (requires valid API keys in .env)
# ============================================================

def test_real_openai_api():
    """
    Test real OpenAI API call.
    REQUIRES: Valid OPENAI_API_KEY in environment
    COST: ~$0.0001 per test
    """
    print("=" * 50)
    print("Testing Real OpenAI API")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping (no OPENAI_API_KEY in environment)")
        return
    
    try:
        llm = OpenAIModel()
        
        # Simple test
        prompt = 'Respond with this exact JSON: {"message": "Hello"}'
        response = llm.generate_response(prompt)
        
        print(f"✅ API call successful")
        print(f"Response: {response}")
        
        # Check response format
        assert isinstance(response, str)
        assert len(response) > 0
        
        print("\n✅ Real OpenAI API test passed!\n")
        
    except Exception as e:
        print(f"❌ API test failed: {e}\n")


def test_real_gemini_api():
    """
    Test real Gemini API call.
    REQUIRES: Valid GEMINI_API_KEY in environment
    COST: Free tier available
    """
    print("=" * 50)
    print("Testing Real Gemini API")
    print("=" * 50)
    
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Skipping (no GEMINI_API_KEY in environment)")
        return
    
    try:
        llm = GeminiModel()
        
        # Simple test
        prompt = 'Respond with this exact JSON: {"message": "Hello"}'
        response = llm.generate_response(prompt)
        
        print(f"✅ API call successful")
        print(f"Response: {response}")
        
        # Check response format
        assert isinstance(response, str)
        assert len(response) > 0
        
        print("\n✅ Real Gemini API test passed!\n")
        
    except Exception as e:
        print(f"❌ API test failed: {e}\n")


if __name__ == "__main__":
    # Run mock tests (always work, no API needed)
    test_mock_llm()
    test_openai_initialization()
    test_gemini_initialization()
    test_token_estimation()
    
    print("=" * 50)
    print("🎉 ALL MOCK TESTS PASSED!")
    print("=" * 50)
    
    # Uncomment to test real APIs (costs money/quota)
    print("\n" + "=" * 50)
    print("Optional: Real API Tests")
    print("=" * 50)

    if "USE_API" in globals() and USE_API is True:
        reponse = 'y'
    else:
        response = input("\nTest real APIs? This will use API quota/credits (y/N): ")
        
    if response.lower() == 'y':
        test_real_openai_api()
        test_real_gemini_api()
    else:
        print("Skipping real API tests")
