#!/usr/bin/env python3

import sys
import base64
import requests
import json
import os
import uuid
import argparse


def read_prompt_from_file(prompt_file_path):
    """Reads the prompt from the specified file."""
    try:
        with open(prompt_file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        sys.exit(1)


IAM_APIKEY_ENV_PROPERTY = os.environ.get("IAM_APIKEY")
# Only exit if we're not in a testing environment
if IAM_APIKEY_ENV_PROPERTY is None and 'pytest' not in sys.modules:
    print("IAM_APIKEY environment variable is not set")
    sys.exit(1)


DEFAULT_BASE_URL = "https://api.dataplatform.cloud.ibm.com/v2/wca/core/chat/text/generation"
DEFAULT_IBM_IAM_URL = "https://iam.cloud.ibm.com/identity/token"


def get_bearer_token(apikey=IAM_APIKEY_ENV_PROPERTY):
    """
    Returns a bearer token for authentication with IBM Cloud services.
    Uses the apikey specified in the IAM_APIKEY environment property

    Args:
        The apikey=None: The apikey to use for authentication.
        If not provided, the value of the IAM_APIKEY environment variable is used.

    Returns:
        str: The bearer token

    Throws an exception if the bearer cannot be obtained
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": apikey}
    response = requests.post(DEFAULT_IBM_IAM_URL, headers=headers, data=data, timeout=30)
    if not response.ok:
        raise Exception(f"Status code: {response.status_code}, Error: {json.loads(response.content)}")
    return response.json()["access_token"]


def call(
    payload,
    file_list=None,
    url=DEFAULT_BASE_URL,
    request_id=str(uuid.uuid4()),
    apikey=IAM_APIKEY_ENV_PROPERTY,
):
    """
    Call the Watson Code Assistant API to get a code completion response.

    Parameters:
    - prompt: The code prompt to send to the API.
    - url: The URL of the Watson Code Assistant API. Defaults to the value of the BASE_URL environment variable,
           or to a default URL if the environment variable is not set.
    - request_id: A unique identifier for the request. Defaults to a randomly generated UUID.
    - apikey: the APIKEY used to authenticate against the url.

    Returns:
    A JSON object containing the code completion response from the API.

    Raises:
    - If the request to the API fails, raises a requests.exceptions.RequestException exception.
    """
    headers = {
        "Authorization": f"Bearer {get_bearer_token(apikey)}",
        "Request-Id": request_id,
        "Origin": "vscode",
    }

    file_list = file_list or []
    files = []
    files.append(("message", (None, json.dumps(payload))))
    for a_file in file_list:
        file_name = a_file.split("/")[-1]
        with open(a_file, "rb") as file:
            encoded_content = base64.b64encode(file.read()).decode("utf-8")
        files.append(("files", (file_name, encoded_content, "text/plain")))
    response = requests.post(url=url, headers=headers, files=files, timeout=180)
    if not response.ok:
        print("response=", response.content, "payload=", payload, "url=", url, "request_id=", request_id)
        response.raise_for_status()
    return response.json()


def build_prompt_payload(text):
    # The API expects the content field to be a string, not a list of dicts.
    # If text is a list, convert it to a JSON string.
    if isinstance(text, list):
        content_str = json.dumps(text)
    else:
        content_str = text
    payload = {
        "message_payload": {
            "messages": [{"content": content_str, "role": "USER"}],
        }
    }
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")
    return payload_base64


def call_api(prompt_str, source_files=None):
    response = call(
        build_prompt_payload(prompt_str),
        apikey=IAM_APIKEY_ENV_PROPERTY,
        file_list=source_files,
    )
    return response["response"]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="Call Watson Code Assistant API")
    parser.add_argument("--diff-file", type=str, help="Path to the diff file", required=True)
    parser.add_argument("--prompt", type=str, help="The prompt for code review")
    parser.add_argument("--prompt-file", type=str, help="Path to a file containing the prompt")
    parser.add_argument(
        "--context-files",
        type=str,
        help="Comma-separated list of paths to context files",
    )
    args = parser.parse_args()
    default_prompt = """
Instructions:
##
Review the attached code and find bugs and issues in the code. Attached diff for review and original files.
Added lines are marked with "+" and removed lines are marked with "-". Lines that are not changed are not marked.
Suggest improvements for the change in the file.
Write exact lines of files that need to be changed. Don't explain the purpose of the original file.
Do not suggest descriptive variable name.
The diff code is below:
##
"""
    if args.prompt_file:
        prompt = read_prompt_from_file(args.prompt_file)
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = default_prompt

    diff_file = args.diff_file
    # Add content of diff file to prompt
    with open(diff_file, "r") as f:
        diff_content = f.read()
        prompt += f"```\n{diff_content}\n```"

    context_files_list = args.context_files.split(",") if args.context_files else []

    review = call_api(prompt, source_files=context_files_list)
    print(review)


if __name__ == "__main__":
    main()
