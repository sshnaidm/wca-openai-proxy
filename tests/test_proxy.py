import os
import sys
import json
import unittest

# Add the tests directory to the path so we can import the mock_watsonai module
sys.path.insert(0, os.path.dirname(__file__))

# Import the mock_watsonai module
import mock_watsonai  # noqa: E402

# Replace the real watsonai module with our mock
sys.modules['watsonai'] = mock_watsonai

# Add the src directory to the path so we can import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Now import the app
from src.watson_openai_proxy import app  # noqa: E402


class TestWatsonOpenAIProxy(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Ensure the API key is set for testing
        os.environ["IAM_APIKEY"] = "test_api_key"

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.app.get("/health")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["model"], "watson-ai")

    def test_list_models(self):
        """Test the models listing endpoint"""
        response = self.app.get("/v1/models")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["object"], "list")
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["id"], "watson-ai")

    def test_chat_completions(self):
        """Test the chat completions endpoint"""

        # Test request data
        request_data = {
            "model": "watson-ai",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
        }

        response = self.app.post("/v1/chat/completions", data=json.dumps(request_data), content_type="application/json")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["choices"][0]["message"]["content"], "This is a test response")
        self.assertEqual(data["model"], "watson-ai")

    def test_completions(self):
        """Test the legacy completions endpoint"""

        # Test request data
        request_data = {"model": "watson-ai", "prompt": "Hello, how are you?"}

        response = self.app.post("/v1/completions", data=json.dumps(request_data), content_type="application/json")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["choices"][0]["text"], "This is a test response")
        self.assertEqual(data["model"], "watson-ai")

    def test_chat_completions_no_user_message(self):
        """Test the chat completions endpoint with no user message"""
        # Test request data with no user message
        request_data = {
            "model": "watson-ai",
            "messages": [{"role": "system", "content": "You are a helpful assistant."}],
        }

        response = self.app.post("/v1/chat/completions", data=json.dumps(request_data), content_type="application/json")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
