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

ignore_list = ["Context_Logs"]

def get_file_paths(directory):
    file_paths = []

    # Traverse the directory recursively
    for root, directories, files in os.walk(directory):
        directories[:] = [d for d in directories if d not in ignore_list] # This will ignore directories in the ignore_list
        for file in files:
            file_path = os.path.join(root, file)
            # Ignore files in ignore_list
            if os.path.basename(file_path) not in ignore_list:
                file_paths.append(file_path)

    return file_paths