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
import re
import traceback

from .log import Log

class Task:
    def __init__(self, filepath, global_context, context_dict, prompts, prompt_outputs, prompt_output_tags):
        self.filepath = filepath
        self.global_context = global_context
        self.context_dict = context_dict
        self.prompts = prompts
        self.prompt_outputs = prompt_outputs
        self.prompt_outputs_tags = prompt_output_tags
    
    def __str__(self):
        return (f'Task(\n'
                f'\tfilepath={self.filepath},\n'
                f'\tglobal_context={self.global_context},\n'
                f'\tcontext_dict={self.context_dict},\n'
                f'\tprompts={self.prompts},\n'
                f'\tprompt_outputs={self.prompt_outputs},\n'
                f'\tprompt_outputs_tags={self.prompt_outputs_tags}\n'
                f')')

regexPatterns = {
    "Global": r"(?s)<context>(.*?)<context/>",
    "Import_Context_Variables": r"(?s)<import>(.*?)<import/>",
    "Import_Specific_Context_Variable": r"(?s)<import:(\w+)>(.*?)<import:\1/>",
    "Import_File_Context_Variables": r"(?s)<file:(\w+)>(.*?)<file:\1/>",
    "Context_Variables": r"(?s)<context:(\w+)>(.*?)<context:\1/>",
    "Prompts": r"(?s)<prompt:([a-zA-Z0-9_]+)>(.*?)<prompt:\1/>",
    "Output_Variables": r".*{(\w+)}.*",   # Allow for characters before and after {}
    "Prompt_Output_Tags": r"(?s)<(?!context|import|file)(\w+)>(.*?)<\1/>"
}

def __tag_parsing_process(path):
    with open(path, 'r') as file:
        content = file.read()

    # Create context_dict, prompts, prompt_outputs, and prompt_outputs_tags
    context_dict = {}
    prompts = {}
    prompt_outputs = []
    prompt_outputs_tags = {}

    # Iterating over the regex patterns
    for tag, pattern in regexPatterns.items():
        matches = re.findall(pattern, content)  # Use content for all matches

        if tag == "Global" and len(matches) > 1:
            raise ValueError(f"Multiple Global tags found in file {path}")

        if tag == "Import_File_Context_Variables":
            for match in matches:
                varName, filePath = match
                Log.logger.debug(varName + "------" + filePath.strip())
                with open(filePath.strip(), 'r') as file:
                    context_dict[varName] = file.read()

        if tag == "Import_Context_Variables":
            for match in matches:
                import_path = match.strip() if matches else None

                # Parse the file at import_path for context variables and add them to context_dict
                Log.logger.debug("IMPORT CONTEXT: -----------" + import_path) 
                with open(import_path, 'r') as file:
                    import_content = file.read()
                    import_context_variables = re.findall(regexPatterns["Context_Variables"], import_content)
                    for import_varName, import_varContent in import_context_variables:
                        context_dict[import_varName] = import_varContent.strip()

        if tag == "Import_Specific_Context_Variable":
            for match in matches:
                varName = match[0]
                import_path = match[1].strip()

                # Parse the file at import_path for the specific context variable and add it to context_dict
                Log.logger.debug("IMPORT SPECIFIC CONTEXT: -----------" + import_path + "----" + varName) 
                with open(import_path, 'r') as file:
                    import_content = file.read()
                    import_context_variable = re.findall(f"(?s)<context:{varName}>(.*?)<context:{varName}/>", import_content)
                    if import_context_variable:
                        context_dict[varName] = import_context_variable[0].strip()

        elif tag == "Global":
            global_context = matches[0][0].strip() if matches else None
        elif tag == "Context_Variables":
            for match in matches:
                context_dict[match[0]] = match[1].strip()
        elif tag == "Prompts":
            for match in matches:
                prompts[match[0]] = match[1].strip()
                
        elif tag == "Prompt_Output_Tags":
            for match in matches:
                varName = match[0]
                tag_content = match[1]
                
                if varName in context_dict:
                    raise ValueError(f"Prompt output variable '{varName}' already exists in context_dict in file {path}")
                
                prompt_outputs_tags[varName] = tag_content.strip()

    # After processing all other tags, remove all prompts from the content
    content_without_prompts = content
    for prompt_name, prompt_content in prompts.items():
        prompt = "<prompt:" + prompt_name + ">" + prompt_content + "<" + "<prompt:" + prompt_name + "/>"
        content_without_prompts = content_without_prompts.replace(prompt, '')
    Log.logger.debug("Content without prompts:\n" + content_without_prompts)

    # Process output variables separately to exclude context variables
    # Instead of running the regex initially, just loop through all prompts at the end,
    # and try to find {PromptName}, anywhere in the content_without_prompts.
    # If found then check if the {PromptName} is inside the prompt content. 
    # If it is inside the prompt content then skip.
    # If it is not then add it to prompt_outputs.
    for prompt_name in prompts.keys():
        pattern = f"{{{re.escape(prompt_name)}}}"
        if re.search(pattern, content_without_prompts):
            Log.logger.debug(f"Found {prompt_name} in content_without_prompts")
            if pattern not in prompts[prompt_name]:
                Log.logger.debug(f"Adding {prompt_name} to prompt_outputs")
                prompt_outputs.append(prompt_name)
            else:
                Log.logger.debug(f"Skipping {prompt_name} because it is inside the prompt content")
        else:
            Log.logger.debug(f"{prompt_name} not found in content_without_prompts")

    # A Task is only created if there are prompts in the file
    return Task(path, global_context, context_dict, prompts, prompt_outputs, prompt_outputs_tags) if len(prompts) > 0 else None

def parse_tags(file_paths, in_comment_signs):
    tasks = []
    comment_signs = in_comment_signs

    for path in file_paths:
        # try:
        task = __tag_parsing_process(path)
        if task is not None:
            tasks.append(task)
        # except IOError:
        #     Log.logger.debug(f"Could not read file: {path}")
        # except ValueError as ve:
        #     Log.logger.debug("An error occurred during tag parsing:")
        #     Log.logger.debug(traceback.format_exc())
        #     continue

    return tasks