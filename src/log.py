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
import logging
from datetime import datetime

class Log():
    logger = None

def configure_logger(debug, logToFile):

    # Set level to DEBUG if debug is True, otherwise set level to INFO.
    log_level = logging.DEBUG if debug else logging.INFO

    # Define the log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # If logToFile is True, create a new directory (if necessary) and log to a new file.
    if logToFile:
        if not os.path.exists('Context_Logs'):
            os.makedirs('Context_Logs')

        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        log_file = f'Context_Logs/context_log_{timestamp}.txt'
        logging.basicConfig(level=log_level, format=log_format, filename=log_file)

    # If logToFile is False, log to console.
    else:
        logging.basicConfig(level=log_level, format=log_format)

    return logging.getLogger(__name__)

