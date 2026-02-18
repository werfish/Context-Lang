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
import argparse
import os
import textwrap
from collections import defaultdict

from colorama import Fore, Style, init
from dotenv import load_dotenv

from .ast import PromptDependencyCycleError, build_prompt_order
from .code_generator import generate_code
from .config import Config
from .file_manager import get_file_paths
from .log import Log, configure_logger
from .tag_parser import parse_tags

logger = None


def entryArguments():
    parser = argparse.ArgumentParser(description="Process a file using Context.")

    parser.add_argument("--debug", action="store_true", help="Debug mode (optional)", required=False, default=False)

    parser.add_argument("--log", action="store_true", help="Log to file (optional)", required=False, default=False)

    parser.add_argument(
        "--parser", action="store_true", help="Parser only mode (optional)", required=False, default=False
    )

    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Mock LLM responses (for tests). Skips API key validation.",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--filepath",
        metavar="filepath",
        type=str,
        help="the path to the file to be processed (optional)",
        required=False,
    )

    parser.add_argument(
        "--openrouter_key", metavar="openrouter_key", type=str, help="the OpenRouter API key (optional)", required=False
    )

    parser.add_argument(
        "--model",
        metavar="model",
        type=str,
        help="OpenRouter model (optional)",
        required=False,
        choices=Config.Supported_Models,
        default=Config.Model,
    )

    args = parser.parse_args()

    return args


def configurationProcess(args):
    dotenv_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path)

    Config.Debug = args.debug
    Config.Log = args.log
    Config.ParserOnly = args.parser
    Config.MockLLM = getattr(args, "mock_llm", False)

    if args.openrouter_key is not None:
        Config.Api_Key = args.openrouter_key
    else:
        Config.Api_Key = os.getenv("CONTEXT_CONFIG_Open_Router_Api_Key")

    Config.Model = args.model

    # Config.Comment_Characters = str(os.getenv("CONTEXT_CONFIG_Comment_Characters")).replace("'","").split(",")

    if not Config.MockLLM and Config.Api_Key is None:
        raise ValueError(
            "OpenRouter API Key is required. Please provide it as an argument, "
            "environment variable or in the .env file."
        )

    if args.filepath is not None:
        Config.FilePathProvided = True
        Config.FilePath = args.filepath


def contextProcess():
    Log.logger.debug("CWD: " + os.getcwd())
    Log.logger.debug("Processing the Files")

    paths = []
    if Config.FilePathProvided is False:
        paths = get_file_paths(os.getcwd())
    else:
        if os.path.isdir(Config.FilePath):
            Log.logger.debug(f"Directory provided: {Config.FilePath}")
            paths = get_file_paths(Config.FilePath)
        else:
            paths = [Config.FilePath]

    Log.logger.debug(paths)

    try:
        tasks, errors = parse_tags(paths, Config.Comment_Characters)
        Log.logger.debug("\nTASKS")
        for task in tasks:
            Log.logger.debug(task)
        if errors:  # If there are any collected errors
            print_formatted_errors(errors)
            return  # Exit the process after printing errors
    except Exception as e:
        # Here, we log the full exception with stack trace
        Log.logger.error("An unexpected error occurred during the process.", exc_info=True)
        # And then print a more user-friendly message
        print(f"Error encountered: {e}. Please check the log for more details.")
        return  # Exiting or handling error as needed

    if Config.ParserOnly:
        return None

    # Semantic parsing (AST prompt ordering): collect per-file errors so the user can fix them in one pass.
    ast_errors = []
    for task in tasks:
        try:
            build_prompt_order([task])
        except PromptDependencyCycleError as e:
            rel_path = os.path.relpath(getattr(e, "filepath", None) or task.filepath)
            cyclic = getattr(e, "cyclic_prompts", None) or []
            cyclic_part = f" Cyclic prompts: {cyclic}." if cyclic else ""
            msg = (
                "AST: prompt dependency cycle detected." + cyclic_part + " Prompt ordering requires an acyclic graph. "
                "Break the cycle by splitting prompts into a one-way chain (e.g., A depends on B depends on C), "
                "or remove the circular {PromptName} references."
            )
            ast_errors.append(f"Error in file {rel_path}: {msg}")
            Log.logger.error(msg)
        except Exception as e:
            # Keep behavior safe and user-friendly; we still include the file context.
            rel_path = os.path.relpath(task.filepath)
            msg = f"AST: unexpected error while ordering prompts: {e}"
            ast_errors.append(f"Error in file {rel_path}: {msg}")
            Log.logger.error(msg, exc_info=True)

    if ast_errors:
        print_formatted_errors(ast_errors)
        return

    generate_code(tasks)


def print_formatted_errors(errors):
    # Group errors by file
    errors_by_file = defaultdict(list)
    for error in errors:
        path, error_message = error.split(": ", 1)
        rel_path = path.replace("Error in file ", "")
        errors_by_file[rel_path].append(error_message)

    # Print errors grouped by file
    for file, error_messages in sorted(errors_by_file.items()):
        print(f"{Fore.CYAN}./{file}{Style.RESET_ALL}")
        error_count = 0  # Initialize error count for each file
        for message in error_messages:
            wrapped_message = textwrap.fill(message, width=70, subsequent_indent=" " * 9)
            print(f"{Fore.RED}         • {wrapped_message}{Style.RESET_ALL}")
            error_count += 1  # Increment error count for each error
        # Print summary line for each file
        print(f"{Fore.YELLOW}Total errors in {file}: {error_count}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'-'*80}{Style.RESET_ALL}")  # Line separator for visual separation


def main():
    # Initialize Colorama
    init(autoreset=True)

    # Handle entry arguments
    args = entryArguments()

    # Create configuration
    configurationProcess(args)

    # Setup the logging
    Log.logger = configure_logger(Config.Debug, Config.Log)

    # Checking for OpenRouter Key
    Log.logger.debug(f"Processing file: {args.filepath}")
    if args.openrouter_key:
        Log.logger.debug("Using provided OpenRouter key.")

    Log.logger.debug(f"Using OpenRouter model: {Config.Model}")

    # Run the context process
    contextProcess()

    Log.logger.info("PROCESSING SUCCESFULL!!!")


if __name__ == "__main__":
    main()
