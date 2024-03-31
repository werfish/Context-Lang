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
from dotenv import load_dotenv
import os
from collections import defaultdict
from colorama import init, Fore, Style
import textwrap

from .config import Config
from .file_manager import get_file_paths
from .tag_parser import parse_tags
from .code_generator import generate_code
from .log import Log,configure_logger

logger = None

def entryArguments():
    parser = argparse.ArgumentParser(description='Process a file using Context.')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Debug mode (optional)',
                        required=False,
                        default=False)

    parser.add_argument('--log',
                        action='store_true',
                        help='Log to file (optional)',
                        required=False,
                        default=False)
    
    parser.add_argument('--parser',
                        action='store_true',
                        help='Parser only mode (optional)',
                        required=False,
                        default=False)

    parser.add_argument('--filepath',
                        metavar='filepath',
                        type=str,
                        help='the path to the file to be processed (optional)',
                        required=False)

    parser.add_argument('--openai_key',
                        metavar='openai_key',
                        type=str,
                        help='the OpenAI API key (optional)',
                        required=False)

    args = parser.parse_args()

    return args

def configurationProcess(args):
    dotenv_path = os.path.join(os.getcwd(), '.env')
    if not load_dotenv(dotenv_path):
        raise FileNotFoundError("No .env file found in the current working directory.")
    
    Config.Debug = args.debug
    Config.Log = args.log
    Config.ParserOnly = args.parser

    if args.openai_key is not None:
        Config.Api_Key= args.openai_key
    else:
        Config.Api_Key = os.getenv("CONTEXT_CONFIG_Open_Ai_Api_Key")

    #Config.Comment_Characters = str(os.getenv("CONTEXT_CONFIG_Comment_Characters")).replace("'","").split(",")

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

    if(Config.ParserOnly):
        return None

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
        for message in error_messages:
            wrapped_message = textwrap.fill(message, width=70, subsequent_indent=' ' * 9)
            print(f"{Fore.RED}         • {wrapped_message}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'-'*80}{Style.RESET_ALL}")  # Line separator for visual separation
    
def main():
    # Initialize Colorama
    init(autoreset=True)

    #Handle entry arguments
    args = entryArguments()

    #Create configuration
    configurationProcess(args)

    #Setup the logging
    Log.logger = configure_logger(Config.Debug, Config.Log)

    #Checking for Open AI Key
    Log.logger.debug(f"Processing file: {args.filepath}")
    if args.openai_key:
        Log.logger.debug(f"Using provided OpenAI key.")

    #Run the context process
    contextProcess()

    Log.logger.info("PROCESSING SUCCESFULL!!!")

if __name__ == '__main__':
    main()