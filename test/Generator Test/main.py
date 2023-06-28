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

#python
def some_function(a, b):
    #Doing something
    return a + b

#{GeneratePythonFunction}


# <PANDAS_CODE>
# <PANDAS_CODE/>