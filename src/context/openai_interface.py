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
from openai import OpenAI
import requests

from .config import Config
from .log import Log

prompts ={
    "System": """You are a Coding Assistant. Your main role is to generate code based on user commands and context information. When specific <<<TAGNAME>>> <<<TAGNAME>>>/ markers are present in the input code, generate and return new functions or modifications to be inserted directly between these tags only, without altering any other part of the code. If no such markers are present, it indicates a request for refactoring or comprehensive code generation. In this case, please provide a full implementation of the code with all requested features and optimizations.

Follow these specific guidelines:
- Describe code and any modifications by embedding comments in code blocks.
- Focus on generating accurate, efficient code based on the provided instructions and context.
- Return the whole modified code if no specific tags guide the insertion or modification point.

Remember, your goal is to assist in generating accurate, efficient code based on the provided instructions and context."""
,
    "System2":"""You are a coding assistant. The USER will give you instructions to help write code 
    You may ask for clarification if needed, but otherwise you should only output code. 
    Provide explanations of the code inside the code by utilising comments only if the user asks for them.""",
    "System3": """You are an advanced Coding Assistant specializing in generating and refining code segments based on specific, 
    detailed context information and templates provided in the instructions. Your output should seamlessly integrate with existing code, 
    adhering to best coding practices. If necessary, suggest improvements or seek more context to ensure the generated code meets the highest 
    standards of accuracy and efficiency. You may provide explanatory comments only if explicitly requested.
"""
}

JsonSystemPrompt = """
You are a Code Scraper Assistant, adept at extracting and refining code from mixed content. 
Your task is to identify, format, and output code segments from the provided content accurately. 
Ensure the code is clean, well-formatted, and ready for integration into a larger codebase. 
Pay special attention to maintaining the integrity and structure of the code as intended in the original generation request.
"""

JsonPrompt = """
Please use the function to output the code of the program from the content.

CONTENT_CONTAINING_CODE:
"""

functions = [
    {
        "name": "scrape_code",
        "description": "Scrape code from user input.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "code text without code block characters",
                }
            },
            "required": ["code"],
        },
    }
]

GPT_MODEL = "gpt-4-1106-preview"

def generate_code_with_chat(prompt,prompt_name):
    Log.logger.debug(f"Generated Prompt:\n{prompt}")
    messages = [
        {"role": "system", "content": prompts["System"].replace("<<<TAGNAME>>>", prompt_name)},
        {"role": "user", "content": prompt}
    ]

    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=Config.Api_Key,
        )
        response = client.chat.completions.create(
            model = GPT_MODEL, #"gpt-3.5-turbo-0301" , #"gpt-4-0613",  # Use the new GPT-4 model
            messages=messages
        )
    except Exception as e:
        Log.logger.error("Unable to generate ChatCompletion response")
        Log.logger.error(f"Exception: {e}")
        raise

    messagesJson = [
        {"role": "system", "content": JsonSystemPrompt},
        {"role": "user", "content": JsonPrompt + "\n" + response.choices[0].message.content}
    ]

    response2 = chat_completion_request(
        messagesJson, functions=functions
    )
    # Extract the generated code
    Log.logger.debug("OPEN API RESPONSE------------------------------")
    Log.logger.debug(response.choices[0].message.content)
    Log.logger.debug("---------------------------------------")
    Log.logger.debug("JSON RESPONSE----------------------------")
    Log.logger.debug(response2.json()["choices"][0]["message"]["function_call"]["arguments"])
    Log.logger.debug("------------------------------------------")
    code = response2.json()["choices"][0]["message"]["function_call"]["arguments"]
    return code

def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + Config.Api_Key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        Log.logger.debug("FUNCTION RESPONSE---------------------------------------------------------------")
        Log.logger.debug(response.json()["choices"][0])
        Log.logger.debug("--------------------------------------------------------------------------------")
        return response
    except Exception as e:
        Log.logger.error("Unable to generate ChatCompletion response")
        Log.logger.error(f"Exception: {e}")
        raise