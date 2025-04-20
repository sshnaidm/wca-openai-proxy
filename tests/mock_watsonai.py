"""
Mock implementation of the watsonai module for testing purposes.
"""


def get_bearer_token(apikey=None):
    """Mock implementation of the get_bearer_token function."""
    return "mock_token"


def build_prompt_payload(text):
    """Mock implementation of the build_prompt_payload function."""
    return "mock_payload"


def call(payload, file_list=None, url=None, request_id=None, apikey=None):
    """Mock implementation of the call function."""
    return {
        "response": {
            "message": {
                "content": "This is a test response"
            }
        }
    }
