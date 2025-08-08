import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""



def main():
    load_dotenv()

    args = sys.argv[1:]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here"')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)
    user_prompt = " ".join(args)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    if "--verbose" in args:
        print("Verbose mode enabled.")
        generate_content_verbose(client, messages, user_prompt)
    else:
        generate_content(client, messages)


available_functions = types.Tool(
    function_declarations=[schema_get_files_info]
)


def generate_content(client, messages):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )
    _print_or_calls(response)


def generate_content_verbose(client, messages, user_prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )
    _print_or_calls(response)
    print(f"User prompt: {user_prompt}")
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)


def _print_or_calls(response):
    calls = []
    for cand in getattr(response, "candidates", []) or []:
        content = getattr(cand, "content", None)
        parts = getattr(content, "parts", []) if content else []
        for part in parts or []:
            fc = getattr(part, "function_call", None)
            if fc:
                calls.append(fc)

    if calls:
        for fc in calls:
            # fc.args is already a dict-like; printing it shows single quotes the CLI expects
            print(f"Calling function: {fc.name}({fc.args})")
    else:
        # fallback: just show the text
        print("Response:")
        print(response.text)


if __name__ == "__main__":
    main()