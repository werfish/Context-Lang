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
import openai
from config import Config
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests

from log import Log

prompts ={
    "System": """You are a Coding Assistant. Your main role is to generate code based on user commands and context information. The code generated by your output will be pasted directly into a file. You may not have all the information regarding the rest of the file.

Follow these specific guidelines:
- You can describe code by embedding comments in code blocks.
- You should return the whole modified code if the user asks for it.

Remember, your goal is to assist in generating accurate, efficient code based on the provided instructions and context.
""",
    "System2":"""You are a coding assistant. The USER will give you instructions to help write code 
    You may ask for clarification if needed, but otherwise you should only output code. 
    Provide explanations of the code inside the code by utilising comments only if the user asks for them."""
}

JsonSystemPrompt = """
You are a code scraper assistant. You help users extract code in any programming lanuguage from
user provided content which can contain code and text.
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

GPT_MODEL = "gpt-3.5-turbo-0613"

def generate_code_with_chat(prompt):
    Log.logger.debug(f"Generated Prompt:\n{prompt}")
    openai.api_key = Config.Api_Key
    messages = [
        {"role": "system", "content": prompts["System"]},
        {"role": "user", "content": prompt}
    ]

    try:
        response = openai.ChatCompletion.create(
            model= "gpt-3.5-turbo-0301" , #"gpt-4-0613",  # Use the new GPT-4 model
            messages=messages
        )
    except Exception as e:
        Log.logger.error("Unable to generate ChatCompletion response")
        Log.logger.error(f"Exception: {e}")
        raise

    messagesJson = [
        {"role": "system", "content": JsonSystemPrompt},
        {"role": "user", "content": JsonPrompt + "\n" +response.choices[0].message['content']}
    ]

    response2 = chat_completion_request(
        messagesJson, functions=functions
    )
    # Extract the generated code
    Log.logger.debug("OPEN API RESPONSE------------------------------")
    Log.logger.debug(response.choices[0].message['content'])
    Log.logger.debug("---------------------------------------")
    Log.logger.debug("JSON RESPONSE----------------------------")
    Log.logger.debug(response2.json()["choices"][0]["message"]["function_call"]["arguments"])
    Log.logger.debug("------------------------------------------")
    code = response2.json()["choices"][0]["message"]["function_call"]["arguments"]
    return code

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
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