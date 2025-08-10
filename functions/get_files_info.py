import os
from config import MAX_CHARS
from google.genai import types


def get_files_info(working_directory, directory=None):
    abs_working_dir = os.path.abspath(working_directory)
    target_dir = abs_working_dir
    if directory:
        target_dir = os.path.abspath(os.path.join(working_directory, directory))
    if not target_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'
    try:
        files_info = []
        for filename in os.listdir(target_dir):
            filepath = os.path.join(target_dir, filename)
            file_size = 0
            is_dir = os.path.isdir(filepath)
            file_size = os.path.getsize(filepath)
            files_info.append(
                f"- {filename}: file_size={file_size} bytes, is_dir={is_dir}"
            )
        return "\n".join(files_info)
    except Exception as e:
        return f"Error listing files: {e}"
    

def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(target_file, "r") as f:
            content = f.read(MAX_CHARS + 1)  
    except Exception as e:
        return f"Error: {e}"
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    return content


def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    parent_dir = os.path.dirname(target_file)
    if parent_dir and not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            return f"Error: {e}"
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"Error: {e}"
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description=(
        "Lists files in the specified directory along with their sizes, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the working "
                    "directory. If not provided, lists files in the working "
                    "directory itself."
                ),
            ),
        },
    ),
)


# Read file contents
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads a file's contents (truncated to a safe limit) within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)

# Write / overwrite a file
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes (creates or overwrites) a file in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Text content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)



    
    