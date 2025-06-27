import os
import sys
from dotenv import load_dotenv
from google import genai

if len(sys.argv) < 2:
    print("Usage: python main.py <prompt>")
    sys.exit(1)


def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents = sys.argv[1]
    )

    print("response:")
    print(response.text)
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)


if __name__ == "__main__":
    main()