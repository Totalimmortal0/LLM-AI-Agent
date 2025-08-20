import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.config import system_prompt
from functions.get_files_info import available_functions
from functions.call_function import call_function

def main():

    argument = sys.argv[1:]

    if not argument:
        print("Please Input a Prompt")
        sys.exit(1)

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(argument)

    messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    try:

        iteration_num = 0
        while iteration_num < 20:

            response = client.models.generate_content(
                    model='gemini-2.0-flash-001', contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
                )

            for candidate in response.candidates:
                messages.append(candidate.content)

            is_verbose = "--verbose" in argument

            if response.function_calls:
                function_list = []
                for respon in response.function_calls:
                    args = respon.args.copy()
                    if respon.name == "run_python_file" and "directory" in args:
                        cmd_parts = args["directory"].split()
                        if cmd_parts:
                            args["file_path"] = cmd_parts[0]
                            args["args"] = cmd_parts[1:]
                        else:
                            args["file_path"] = ""
                            args["args"] = []
                        del args["directory"]

                    if respon.name == "get_file_content" and "directory" in args:
                        args["file_path"] = args["directory"]
                        del args["directory"]

                    function_call_part = types.FunctionCall(name=respon.name, args=args)
                    function_list.append(call_function(function_call_part, verbose=is_verbose))

                function_list_parts = []
                for parts in function_list:
                    function_list_parts.extend(parts.parts)
                messages.append(types.Content(role="user", parts=function_list_parts))
                
            if response.text and not response.function_calls:
                print(response.text)
                if is_verbose:
                    print(f"User prompt: {user_prompt}")
                    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
                break
            else:
                iteration_num += 1
            
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
if __name__ == "__main__":
    main()
