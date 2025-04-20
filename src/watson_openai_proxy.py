from flask import Flask, request, jsonify, Response
import os
import json
import time
import logging
from watsonai import call, build_prompt_payload

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
DEFAULT_MODEL = "watson-ai"
WATSON_API_KEY = os.environ.get("IAM_APIKEY")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))


def convert_messages_to_prompt(messages):
    prompt_parts = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if not content:
            continue  # skip messages with no content (e.g., tool calls)

        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: ##\n{content}\n##")
        else:
            prompt_parts.append(f"{role.capitalize()}: {content}")  # fallback
    prompt_parts.append("Assistant:")
    return "\n".join(prompt_parts)


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    # Get request data
    data = request.json

    # Check for streaming request
    stream = data.get("stream", False)

    # Extract messages from OpenAI format
    messages = data.get("messages", [])
    user_messages = [msg for msg in messages if msg["role"] == "user"]

    if not user_messages:
        return jsonify({"error": "No user messages provided"}), 400

    prompt = convert_messages_to_prompt(messages)
    # Get file_list if provided
    file_list = data.get("file_list", None)

    try:
        # Call Watson AI
        watson_response = call(build_prompt_payload(prompt), apikey=WATSON_API_KEY, file_list=file_list)

        # Convert to OpenAI format
        content = watson_response["response"]["message"]["content"]
    except Exception as e:
        logger.error(f"Error calling Watson AI API: {str(e)}")
        return (
            jsonify({"error": {"message": f"Error processing request: {str(e)}", "type": "api_error", "code": 500}}),
            500,
        )

    if stream:
        # Implement streaming response
        def generate():
            # Split content into chunks for streaming
            chunks = [content[i : i + 20] for i in range(0, len(content), 20)]

            for i, chunk in enumerate(chunks):
                completion_chunk = {
                    "choices": [
                        {
                            "delta": {"content": chunk},
                            "index": 0,
                            "finish_reason": "stop" if i == len(chunks) - 1 else None,
                        }
                    ],
                    "model": DEFAULT_MODEL,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                }

                yield f"data: {json.dumps(completion_chunk)}\n\n"
                time.sleep(0.01)  # Simulate streaming delay

            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype="text/event-stream")
    else:
        # Return standard response
        return jsonify(
            {
                "choices": [
                    {"message": {"role": "assistant", "content": content}, "index": 0, "finish_reason": "stop"}
                ],
                "id": "chatcmpl-" + os.urandom(4).hex(),
                "model": DEFAULT_MODEL,
                "object": "chat.completion",
                "created": int(time.time()),
                "usage": {
                    "prompt_tokens": len(prompt.split()),  # Approximation
                    "completion_tokens": len(content.split()),  # Approximation
                    "total_tokens": len(prompt.split()) + len(content.split()),  # Approximation
                },
            }
        )


@app.route("/v1/models", methods=["GET"])
def list_models():
    """Return a list of available models (just Watson AI in this case)"""
    return jsonify(
        {
            "object": "list",
            "data": [{"id": DEFAULT_MODEL, "object": "model", "created": int(time.time()), "owned_by": "watson"}],
        }
    )


@app.route("/v1/completions", methods=["POST"])
def completions():
    """Legacy completions endpoint for older tools"""
    data = request.json
    prompt = data.get("prompt", "")

    try:
        watson_response = call(build_prompt_payload(prompt), apikey=WATSON_API_KEY)

        content = watson_response["response"]["message"]["content"]
    except Exception as e:
        logger.error(f"Error calling Watson AI API: {str(e)}")
        return (
            jsonify({"error": {"message": f"Error processing request: {str(e)}", "type": "api_error", "code": 500}}),
            500,
        )

    return jsonify(
        {
            "choices": [{"text": content, "index": 0, "finish_reason": "stop"}],
            "id": "cmpl-" + os.urandom(4).hex(),
            "model": DEFAULT_MODEL,
            "object": "text_completion",
            "created": int(time.time()),
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split()),
            },
        }
    )


@app.route("/health", methods=["GET"])
@app.route("/v1/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    if not WATSON_API_KEY:
        return jsonify({"status": "error", "message": "IAM_APIKEY environment variable is not set"}), 500

    return jsonify({"status": "ok", "version": "1.0.0", "model": DEFAULT_MODEL})


if __name__ == "__main__":
    # Check if API key is set
    if not WATSON_API_KEY:
        logger.error("IAM_APIKEY environment variable is not set")
        exit(1)

    logger.info("Starting OpenAI-compatible proxy server for Watson AI")
    logger.info(f"Available models: {DEFAULT_MODEL}")
    logger.info(f"Server running on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
