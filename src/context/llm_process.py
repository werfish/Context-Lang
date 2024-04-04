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
import os
from langchain.openai import ChatOpenAI
from langchain.llms import LLM
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from tenacity import retry, wait_random_exponential, stop_after_attempt

from .config import Config
from .log import Log

code_generator_system = """
You are a Coding Assistant. Your main role is to generate code based on user commands and context information. When specific <{tagname}> and <{tagname}/> markers are present in the input code, generate and return new functions or modifications to be inserted directly between these tags only, without altering any other part of the code. If no such markers are present, it indicates a request for refactoring or comprehensive code generation. In this case, please provide a full implementation of the code with all requested features and optimizations.

Follow these specific guidelines:
- Describe code and any modifications by embedding comments in code blocks.
- Focus on generating accurate, efficient code based on the provided instructions and context.
- Return the whole modified code if no specific tags guide the insertion or modification point.

Remember, your goal is to assist in generating accurate, efficient code based on the provided instructions and context.
"""
human_template = "{text}"

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


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def generate_code_with_chat(prompt, prompt_name):
    Log.logger.debug(f"Generated Prompt:\n{prompt}")
    # Initialize the ChatOpenAI model with the GPT-4 model you are using
    chat_model = ChatOpenAI(model=GPT_MODEL, openai_api_key=Config.Api_Key)

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", code_generator_system),
            ("human", human_template),
        ]
    )

    chat_prompt.format_messages(tagname=prompt_name, text=prompt)

    # Invoke the model
    response = chat_model.invoke(messages)

    # Assuming the last message in the response is the AI-generated code
    ai_generated_code = response[-1].content


def chat_completion_request(
    messages, functions=None, function_call=None, model=GPT_MODEL
):
    pass
