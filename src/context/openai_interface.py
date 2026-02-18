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
import json

from .graph import run_generation_graph
from .log import Log


def generate_code_with_chat(prompt, prompt_name):
    Log.logger.debug(f"Generated Prompt:\n{prompt}")

    try:
        generated_code = run_generation_graph(prompt, prompt_name)
    except Exception as e:
        Log.logger.error("Unable to generate graph response")
        Log.logger.error(f"Exception: {e}")
        raise

    Log.logger.debug("OPENROUTER RESPONSE------------------------------")
    Log.logger.debug(generated_code)
    Log.logger.debug("---------------------------------------")

    return json.dumps({"code": generated_code})
