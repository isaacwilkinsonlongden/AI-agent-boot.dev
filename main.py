import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Tool function imports + schemas
from functions.get_files_info import (
    get_files_info,
    get_file_content,
    write_file,
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
)
from functions.run_python import (
    run_python_file,
    schema_run_python_file,
)

system_prompt = """
You are a helpful AI coding agent.

You have complete freedom to use the available tools without asking the user for clarification unless it is absolutely impossible to proceed.
When the user asks about code behavior or project structure, proactively inspect likely files and directories using the available tools until you can answer directly.
Never ask the user to identify file paths; decide what to inspect based on their question.

You can perform the following operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

Rules for function calls:
- Always include the required arguments for the chosen function.
- Use 'directory': '.' for the root (working directory) when listing.
- Paths must be relative (no absolute paths or parent traversal).
- For run_python_file, include 'args' only if the user supplied arguments.
- You may chain multiple function calls to gather enough context before answering.

Examples:
- "what files are in the root?" -> get_files_info({'directory': '.'})
- "what files are in the pkg directory?" -> get_files_info({'directory': 'pkg'})
- "read the contents of main.py" -> get_file_content({'file_path': 'main.py'})
- "write 'hello' to main.txt" -> write_file({'file_path': 'main.txt', 'content': 'hello'})
- "run main.py" -> run_python_file({'file_path': 'main.py'})
- "run main.py with 3 + 5" -> run_python_file({'file_path': 'main.py', 'args': ['3 + 5']})
"""


# Expose tool declarations to the model
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# Name -> function map for execution
FUNCTIONS = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False):
    name = function_call_part.name
    args = dict(function_call_part.args or {})

    if verbose:
        print(f"Calling function: {name}({args})")
    else:
        print(f" - Calling function: {name}")

    # Inject sandboxed working directory
    args["working_directory"] = "calculator"

    fn = FUNCTIONS.get(name)
    if not fn:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=name,
                    response={"error": f"Unknown function: {name}"},
                )
            ],
        )

    try:
        result = fn(**args)
    except Exception as e:
        result = f"Error: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=name,
                response={"result": result},
            )
        ],
    )


def run_agent(client, user_prompt, verbose=False):
    # Rolling conversation history
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    for _ in range(20):  # safety cap
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,  # always pass the full conversation
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt,
                ),
            )
        except Exception as e:
            print(f"Error: failed LLM call: {e}")
            return

        # Record the model's reply (all candidates) into the conversation
        candidates = getattr(response, "candidates", []) or []
        for cand in candidates:
            content = getattr(cand, "content", None)
            if content:
                messages.append(content)

        # Extract function calls (if any)
        function_calls = []
        for cand in candidates:
            content = getattr(cand, "content", None)
            for part in (getattr(content, "parts", []) or []):
                fc = getattr(part, "function_call", None)
                if fc:
                    function_calls.append(fc)

        if not function_calls:
            # No tool calls → final answer
            print("Final response:")
            print(response.text)
            return

        # Execute requested tools; append tool responses to the conversation
        for fc in function_calls:
            tool_msg = call_function(fc, verbose=verbose)  # prints call; returns types.Content
            messages.append(tool_msg)

            # Show function results in verbose mode (CLI greps these substrings)
            if verbose:
                parts = getattr(tool_msg, "parts", []) or []
                fr = getattr(parts[0], "function_response", None) if parts else None
                if fr and hasattr(fr, "response"):
                    print(f"-> {fr.response}")

    print("Error: reached max iterations without a final response.")


def main():
    load_dotenv()

    args = sys.argv[1:]
    verbose = False
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here"')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    user_prompt = " ".join(args)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if verbose:
        print("Verbose mode enabled.")
    run_agent(client, user_prompt, verbose=verbose)


if __name__ == "__main__":
    main()
