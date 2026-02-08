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

from .log import Log

_PLACEHOLDER_PATTERN = re.compile(r"{(\w+)}")


def build_prompt_order(tasks):
    for task in tasks:
        try:
            task.prompt_order, task.prompt_layers = _order_prompts(task)
        except Exception as e:
            Log.logger.error(
                f"Failed to build prompt order for {task.filepath}: {e}",
                exc_info=True,
            )
            task.prompt_order = list(task.prompts.keys())
            task.prompt_layers = [task.prompt_order]


def _order_prompts(task):
    prompt_names = list(task.prompts.keys())
    dependencies = {name: set() for name in prompt_names}

    for prompt_name, prompt_content in task.prompts.items():
        placeholders = _PLACEHOLDER_PATTERN.findall(prompt_content)
        for placeholder in placeholders:
            if placeholder in task.prompts and placeholder != prompt_name:
                dependencies[prompt_name].add(placeholder)

    ready = [name for name, deps in dependencies.items() if not deps]
    processed = []
    layers = []
    remaining = {name: set(deps) for name, deps in dependencies.items()}

    while ready:
        current_layer = []
        for name in list(ready):
            ready.remove(name)
            current_layer.append(name)
            processed.append(name)
            for other_name, deps in remaining.items():
                if name in deps:
                    deps.remove(name)
                    if not deps and other_name not in processed and other_name not in ready:
                        ready.append(other_name)
        if current_layer:
            layers.append(current_layer)

    remaining_prompts = [name for name in prompt_names if name not in processed]
    if remaining_prompts:
        Log.logger.warning(
            "Dependency cycle detected in prompts from %s. "
            "Falling back to original order for remaining prompts.",
            task.filepath,
        )
        processed.extend(remaining_prompts)
        layers.append(remaining_prompts)

    return processed, layers
