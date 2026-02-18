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

from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.graph import END, START, StateGraph

from .config import Config


class GraphState(TypedDict):
    prompt: str
    prompt_name: str
    response: str


PROMPTS = {
    "System": """You are a Coding Assistant. Your main role is to generate code based on user commands and context information. When specific <<<TAGNAME>>> <<<TAGNAME>>>/ markers are present in the input code, generate and return new functions or modifications to be inserted directly between these tags only, without altering any other part of the code. If no such markers are present, it indicates a request for refactoring or comprehensive code generation. In this case, please provide a full implementation of the code with all requested features and optimizations.

Follow these specific guidelines:
- Describe code and any modifications by embedding comments in code blocks.
- Focus on generating accurate, efficient code based on the provided instructions and context.
- Return the whole modified code if no specific tags guide the insertion or modification point.

Remember, your goal is to assist in generating accurate, efficient code based on the provided instructions and context."""
}


def _call_openrouter(state: GraphState) -> GraphState:
    llm = ChatOpenRouter(
        api_key=Config.Api_Key,
        model=Config.Model,
    )

    messages = [
        SystemMessage(content=PROMPTS["System"].replace("<<<TAGNAME>>>", state["prompt_name"])),
        HumanMessage(content=state["prompt"]),
    ]
    response = llm.invoke(messages)
    content = response.content if isinstance(response, AIMessage) else str(response)
    return {**state, "response": content}


def build_graph():
    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("openrouter_call", _call_openrouter)
    graph_builder.add_edge(START, "openrouter_call")
    graph_builder.add_edge("openrouter_call", END)
    return graph_builder.compile()


def run_generation_graph(prompt: str, prompt_name: str) -> str:
    graph = build_graph()
    result = graph.invoke({"prompt": prompt, "prompt_name": prompt_name, "response": ""})
    return result["response"]
