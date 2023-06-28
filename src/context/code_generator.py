#    Copyright 2023 Robert Mazurowski

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import traceback
import re
import json

from .openai_interface import generate_code_with_chat
from .log import Log

def generate_code(tasks):
    for task in tasks:
        try:
            __single_file_flow(task)
        except Exception as e:
            Log.logger.debug(f"Error while processing task from file {task.filepath}:")
            traceback.print_exc()

def __single_file_flow(task):
    # If there are no prompt outputs or prompt output tags in the task, skip this task
    if not task.prompt_outputs and not task.prompt_outputs_tags:
        Log.logger.debug(f"No prompt outputs or output tags in task from file {task.filepath}. Skipping this task.")
        return

    # Process each prompt in the task
    for prompt_name, prompt in task.prompts.items():

        # Assemble the prompt
        final_prompt = __process_prompt(prompt, task)

        # Generate the output
        response = generate_code_with_chat(final_prompt)

        # Parse the response JSON
        response_json = json.loads(response)
        
        # Extract the generated code
        code = response_json.get('code', '').strip()

        # For now mock the code change
        Log.logger.debug(f"Generated code for {prompt_name}:\n{code}\n")

        # Apply the code
        __apply_code(code, task, prompt_name)

def __process_prompt(prompt, task):
    # Copy the prompt to avoid modifying the original
    constructedPrompt = prompt

    # Replace {contextVar} in the prompt with contextVar content
    for var_name, var_content in task.context_dict.items():
        placeholder = "{" + var_name + "}"
        formatted_var_content = f"\n\n{var_name}:\n{var_content}"
        constructedPrompt = constructedPrompt.replace(placeholder, formatted_var_content)

    # Replace {contextVar} in the prompt with outputVariables
    for var_name, var_content in task.prompt_outputs_tags.items():
        placeholder = "{" + var_name + "}"
        formatted_var_content = f"\n\n{var_name}:\n{var_content}"
        constructedPrompt = constructedPrompt.replace(placeholder, formatted_var_content)

    # Append global context if present
    if task.global_context:
        constructedPrompt += "\n" + "GLOBAL_CONTEXT:\n" + task.global_context

    return constructedPrompt

def __apply_code(code, task, prompt_name):
    # Open the file and read its contents
    with open(task.filepath, 'r') as file:
        original_code_lines = file.readlines()

    updated_code_lines = original_code_lines.copy()  # create a copy to modify

    # Determine if the prompt output is {} or <>
    if prompt_name in task.prompt_outputs:
        output_placeholder = "{" + prompt_name + "}"

        # Iterate over lines in the original code
        for i, line in enumerate(original_code_lines):
            # If the placeholder is found in this line
            if output_placeholder in line:
                # Replace the entire line with the generated code
                updated_code_lines[i] = code + '\n'  # Add a newline to preserve formatting

    elif prompt_name in task.prompt_outputs_tags:
        start_tag = f"<{prompt_name}>"
        end_tag = f"<{prompt_name}/>"
        
        # Find the lines with the start and end tags
        start_line = next(i for i, line in enumerate(original_code_lines) if start_tag in line)
        end_line = next(i for i, line in enumerate(original_code_lines) if end_tag in line)

        # Replace the lines between the tags with the new code
        # We add a newline character at the end of each line in the generated code
        updated_code_lines[start_line + 1:end_line] = [line + '\n' for line in code.split('\n')]

    else:
        print(f"No output placeholder found for prompt {prompt_name}")
        return

    # Reassemble the lines into a string
    updated_code = ''.join(updated_code_lines)

    Log.logger.debug(f"Final code:\n{updated_code}\n")

    # Overwrite the file with the updated code
    with open(task.filepath, 'w') as file:
        file.write(updated_code)