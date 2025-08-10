import os 
import sys
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_target_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_target_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory.'
    
    if not os.path.exists(abs_target_path):
        return f'Error: File "{file_path}" not found'
    
    if not abs_target_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file'
    
    cmd = [sys.executable, abs_target_path] + list(map(str, args))
    try:
        completed = subprocess.run(
            cmd,
            cwd=abs_working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    parts = []
    if completed.stdout:
        parts.append("STDOUT:\n" + completed.stdout.rstrip())
    if completed.stderr:
        parts.append("STDERR:\n" + completed.stderr.rstrip())
    if completed.returncode != 0:
        parts.append(f"Process exited with code {completed.returncode}")

    if not parts:
        return "No output produced."
    
    return "\n\n".join(parts)


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file in the working directory with optional arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of arguments to pass to the Python file.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)

    