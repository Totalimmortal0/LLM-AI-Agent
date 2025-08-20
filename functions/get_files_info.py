import os
from google.genai import types
from functions.config import system_prompt
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file import schema_write_file

def get_files_info(working_directory, directory="."):
    
    full_path = os.path.join(working_directory, directory)
    
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f' Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(full_path):
        return f' Error: "{directory}" is not a directory'

    try:
        directory_contents = ""
        for direct in os.listdir(full_path):
            file_size = os.path.getsize(os.path.join(full_path, direct))
            is_directory = os.path.isdir(os.path.join(full_path, direct))
            directory_contents += (f" - {direct}: file_size={file_size} bytes, is_dir={is_directory}") + "\n"
        return directory_contents.strip()
    except Exception as e:
        return f"Error: {e}"

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
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

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)