import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    full_path = os.path.join(working_directory, file_path)

    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(full_path):
        return f'Error: File "{file_path}" not found.'
    
    if not full_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        command_list = ["python", file_path]

        if args:
            command_list.extend(args)

        result = subprocess.run(command_list, capture_output=True, timeout=30, cwd=working_directory, text=True)
        formated_string = ""

        if result.stdout:
            formated_string += f"STDOUT: {result.stdout}\n"
        if result.stderr:
            formated_string += f"STDERR: {result.stderr}\n"
        if result.returncode != 0:
            formated_string += f"Process exited with code {result.returncode}\n"
        if formated_string == "":
            return "No output produced."
        return formated_string
    
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute Python files with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)