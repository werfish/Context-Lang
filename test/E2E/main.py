#<file:TABLE>table with data.csv<file:TABLE/>

# <context:TEMPLATE>
def function_name(a,b):
     return a + b
# <context:TEMPLATE/>

#<context:SOMETHING>just some content here<context:SOMETHING/>

# <prompt:GeneratePythonFunction>
# Please generate a multiplication Python function using the template. {TEMPLATE}
# #<prompt:GeneratePythonFunction/>

# <prompt:PANDAS_CODE>
# Please write a function which takes in a path to a csv file and name as argument 
# and filters the csv file by the name and then prints the dataframe. Use the provided schema
# with data examples.
# {TABLE_SCHEMA}
# #<prompt:PANDAS_CODE/>

def function_name(a, b):
    return a * b
#
# #

# <PANDAS_CODE>
import pandas as pd

def filter_csv_by_name(csv_path, name):
    # Assuming 'name' is the column to filter by in your CSV file
    # Replace 'NameColumn' with the actual name of the column in your table schema
    # Define column names as per the table schema provided above:
    # columns = ['Column1', 'Column2', 'NameColumn', 'Column4', ...]
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path, usecols=columns)  # If your CSV file has a header, you can omit `names=columns`
    
    # Filter the DataFrame by the name
    filtered_df = df[df['NameColumn'] == name]
    
    # Print the filtered DataFrame
    print(filtered_df)
    
    # Uncomment and replace 'IndexColumn' with the actual name of the index column if needed
    # filtered_df.set_index('IndexColumn', inplace=True)

# Usage Example:
# Assuming the CSV file path is 'path/to/your/file.csv' and you want to filter by the name 'John Doe'
# filter_csv_by_name('path/to/your/file.csv', 'John Doe')
# <PANDAS_CODE/>