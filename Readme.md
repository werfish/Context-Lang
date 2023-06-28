# Context: AI-Powered Code Generation

Context is a revolutionary AI code preprocessor and generator designed to automate the Chat GPT coding workflow, enabling in-code prompting and output via ContextLang tags embedded in code comments. 

With Context, you can:

0. **Streamline Web Searches During Development**: No more looking up of minute details you don't remember every 30 seconds. Writing code with ContextLang allows for surgical changes to your code based on description of code steps. Let the AI work out the details. Your time spent on web searches during development will significantly decrease.

1. **Automate Chat GPT code modifications**: Say goodbye to the time consuming task of copying and pasting code between the editor and Chat GPT. Forget rewriting descriptions or juggling multiple Chat GPT sessions. Save descriptions as context variables and prompts with ContextLang and reuse both just like you would with code. 

2. **Seamlessly integrate and use**: Context is easy to install, and ContextLang is non invasive, residing within code comments. ContextLang is language-agnostic and fits seamlessly into any programming language and codebase, large or small. Starting with Context is as easy as pie, and integrating it into your existing work requires minimal effort.

3. **Save on cost and time**: Context aims to use 2 Open AI api calls per prompt making daily usage cost mere cents. With Context, you're not just saving time, but also money.

### The Developer is dead, long live the AI augmented cyberpunk developer. The CyDeveloper :)

## Table of Contents
1. [Introduction](#context-ai-powered-code-generation)
2. [Context Description](#context-description)
    - [Goal](#goal)
    - [ContextLang](#contextlang)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Getting Started](#getting-started)
    - [Importing another file as a context variable](#importing-another-file-as-a-context-variable)
    - [Importing a specific context variable existing inside another file](#importing-a-specific-context-variable-existing-inside-another-file)
    - [Importing all context variables from a file](#importing-all-context-variables-from-a-file)
7. [File Template](#file-template)
8. [Best Practices](#best-practices)
9. [Features/Specification V1 (CURRENT)](#featuresspecification-v1-current)
    - [Context Variables](#context-variables)
    - [Prompts](#prompts)
10. [Features/Specification V2 (TO DO)](#featuresspecification-v2-to-do)
11. [Features/Specification V3 (TO DO)](#featuresspecification-v3-to-do)
12. [Documentation](#documentation)
13. [Contributing](#contributing)
14. [License](#license)


## Context Description

Context is a programming tool designed to harness the capabilities of AI to enhance software development. It employs OpenAI's GPT-3.5 Turbo model, uses the custom ContextLang for formatting, and treats contextual descriptions as variables and prompts as functions. This design allows for effective use of AI capabilities, provided the instructions are clear and context is well-described.

Anticipating the development of larger projects such as Engineer-GPT and AutoGPT, which may take years to become practically usable, Context aims to bridge this gap by offering a practical tool for developers to use in their current workflows. It is designed to extract as much as possible from the GPT-3.5 Turbo model until GPT-4 becomes widely accessible. If you already have access to GPT-4, you can use it straight away for potentially better results.

It's important to clarify that Context is not an AI Assistant or an Autonomous Cognitive Entity. It won't ask any questions, work out a design for a project, or carry out reasoning tasks. These elements are left to the human. Context strictly adheres to generating or changing small pieces of code. It effectively replicates the workflow of a Chat GPT frontend, eliminating the need for developers to manually copy the code back and forth and rewrite details or descriptions. As a result, it significantly reduces the manual workload by automating code generation for defined sections.

## Goal

The ambition behind the Context project is to integrate AI into the coding process to make it more efficient and less time-consuming. Context's primary aim is to streamline the initial development phase and make quick fixes more efficient, using the power of AI to achieve these goals. While Context is a powerful tool, it is not a substitute for in-depth knowledge of programming. Developers must still understand their code's logic and thoroughly review all AI-generated code to ensure its correctness and efficiency.

## ContextLang

ContextLang is a domain-specific, declarative language created to interact with the Context tool. Inspired by HTML in its syntax, it's mainly used within code comments but isn't strictly limited to them. ContextLang is employed to structure AI prompts, define code context, and mark areas designated for AI-generated code. Its flexibility and simplicity make it a convenient tool that can be adapted across different programming languages and methodologies.

## Prerequisites

Before installing ContextLang, ensure you have the following:

- [Python](https://www.python.org/downloads/) installed on your system.
- An account on [OpenAI](https://www.openai.com/) with access to the GPT API.
- An API key from OpenAI.

## Installation

Follow these steps to install ContextLang:

1. Install the ContextLang package using pip:

```shell
pip install ContextLang
```

2. In the root folder of your project, create a `.env` file with the following content:

```shell
CONTEXT_CONFIG_Open_Ai_Api_Key=<Your OpenAI API Key here>
```

Remember to replace `<Your OpenAI API Key here>` with your actual API key. The comment characters should match those used in your project. In this example, we've added comment characters for HTML, CSS, and JavaScript.

3. To use Context in your project, navigate to the base folder of your project and run the `Context` command:

```shell
Context
```

If there are no errors, Context is working correctly and is ready for use in your project.

Remember, sensitive information like API keys should not be committed to version control systems. Please ensure to add your `.env` file to `.gitignore` (or equivalent for other VCS) to prevent this.

## Getting Started

The example provided below demonstrates the usage of ContextLang in a Python file to write a simple calculator module.

First, we'll provide a global context to describe the purpose of the file.
Global Context will be injected into every prompt of the file (EXPERIMENTAL):

```python
#<context>This file should contain basic arithmetic functions for a and b.<context/>
```

Next, we will utilize a context variable called "TEMPLATE" to simplify the process of instructing the AI on what we want to achieve. For instance, we'll create a template for an 'addition' function, which the AI can reference when generating other arithmetic functions.

```python
#<context:TEMPLATE>
def add(a,b):
	return a + b
#<context:TEMPLATE/>
```

Now, using a prompt tag, we instruct the AI to create three additional functions for multiplication, division, and subtraction. We provide the previously created template by using the TEMPLATE context variable as a context to guide the AI's output. Keep in mind that global context will also be injected into the prompt. 

```python
#<prompt:Functions>Write me a subtraction, division and multiplication functions for a and b based on the template function. {TEMPLATE} <prompt/>
```
To indicate where the Functions prompt should output we use the name of the prompt enclose in {}. This is a one off operation.The output from the prompt will overwrite the following comment in the Python file when we run Context:

```python
#{Functions}
```

For a more "scratchpad" like experience where a prompt can be iterated with the Functions output variable can also be used as a tag.
This tag will not get overwritten. Only the content between will be overwritten, allowing building up the prompt until it outputs the wanted code.
```python
#<Functions>
#<Functions/>
```

The Functions variable can also be used as context in the prompt while it is used as an output tag, allowing modification over the produced or existing code.
```python
#<prompt:Functions>Please correct the multiply function in the code, it should multiply instead of subtract. {Functions} <prompt/>
#<Functions>
def multiply(a,b):
	return a - b
#OTHER FUNCTIONS....
#<Functions/>
```

Please note that tags of ContextLang do not need to start with `#`. ContextLang should work with most programming language comment characters. Context variables and prompts can be used in txt files. 

Next, we run ContextLang by executing the command `Context` in the base directory of our project. If no errors are thrown, then ContextLang is working as expected, and the `#{Functions}` line in our Python file has been replaced with the output from the prompt.

```shell
Context
```

If you want to run Context on a specific file or a directory then you can use the --filepath argument.

Linux
```shell
Context --filepath ./src
```

Windows
```shell
Context --filepath src
```

### Importing another file as a context variable

Contents of a file can be used like any other context variable.

Syntax Example:
```shell
<file:TABLE_SCHEMA>schema_example.csv<file:TABLE_SCHEMA/>
```

Python file example:

```python
#<file:TABLE_SCHEMA>shema_example.csv<file:TABLE_SCHEMA/>
# <prompt:PANDAS_CODE>
# Please write a function which takes in a path to a csv file and name as arguments 
# and filters the csv file by the name and then prints the dataframe. Use the provided schema with several rows of data as examples.
# {TABLE_SCHEMA}
# <prompt:PANDAS_CODE/>

# <PANDAS_CODE>
#
# <PANDAS_CODE/>
```

### Importing a specific context variable existing inside another file 

Context variables can even be declared in a .txt file. The name of the Context Variable existing in the file needs to be specified.

Syntax:
```shell
<import:INDEX_HTML>index.html<import:INDEX_HTML/>
```

CSS code example:

```css
/*<import:INDEX_HTML>index.html<import:INDEX_HTML/>*/
/*<import:NAVBAR_STYLE>Style_Context.txt<import:NAVBAR_STYLE/>*/

/* <prompt:NavbarStyle>
Please generate css styles for the navbar based on the description according to the ids provided in the HTML code.
{INDEX_HTML}
{NAVBAR_STYLE}
<prompt:NavbarStyle/>*/

/*<NavbarStyle>*/
/*Css code will be generated between the tags*/
/*<NavbarStyle/>*/
```

### Importing all context variables from a file

They can be imported by using the import statement without a context variable name.

```css
/*<import>index.html<import/>*/
/*<import>Style_Context.txt<import/>*/
```

CSS code example:

```css
/*<import:INDEX_HTML>index.html<import:INDEX_HTML/>*/
/*<import:NAVBAR_STYLE>Style_Context.txt<import:NAVBAR_STYLE/>*/

/* <prompt:NavbarStyle>
Please generate css styles for the navbar and the list of links based on the description according to the ids provided in the HTML code.
{INDEX_HTML}
{NAVBAR_STYLE}
{LINKS_LIST}
<prompt:NavbarStyle/>*/

/*<NavbarStyle>*/
/*Css code will be generated between the tags*/
/*<NavbarStyle/>*/

/* <prompt:FooterStyle>
Please generate css styles for the footer based on the description according to the ids provided in the HTML code.
{INDEX_HTML}
{FOOTER_STYLE}
<prompt:FooterStyle/>*/

/*<FooterStyle>*/
/*Css code will be generated between the tags*/
/*<FooterStyle/>*/
```
## File Template
Here is a template that you can copy to your project file. Don't forget to comment it out if using in a code file:).
ContextLang does not yet support comments so If you do not want to use a tag you need to delete it.

Template
```ContextLang
<file:FileContext>example.txt<file:FileContext/>
<import:VarName>file.txt<import:VarName/>
<import>Descriptions.txt<import/>

<context:SomeContext>Some description<context:SomeContext/>
<context:MultiLine>
Some description 
or a piece of code.
<context:MultiLine/>

<prompt:Main>
Prompt Goes here
{SomeContext}
{Multiline}
<prompt:Main/>

<Main>
Code will be generated here.
<Main/>
```

## Best Practices

0. **Be able to code it yourself!!!!!**: If you do not know how to code something manually, then you will usually not be able to describe it accurately. Code generated in this case will be like gambling.

1. **Know CTRL-Z and use git**: Sometimes the code generated will be far from what is needed. Then you need to be able to undo with CTRL-Z or go rollback before a commit if a mistake is made.

2. **Use 1 instruction per prompt**: Use prompts like functions and context like variables. Try to split tasks in more prompts and larger context variables into smaller ones. Deciding how much context GPT needs is an art that will take some time to practice. This is the case for GPT 3.5 Turbo which will rarely follow many detailed instructions. GPT4 however will be able to follow more complex instructions.

3. **Use precise domain oriented language**: Be precise in descriptions. The less space AI has to make up the details, the better. If you develop a web frontend use words that you would use while communicating with other frontend developers.

4. **Split big context variables to smaller ones**: If there is too many instructions in context variables then the AI will fail to deliver all of them. It is better to have 10 context variables and 5 prompts than 3 context variables and 2 prompts.

5. **Use the programming language and library lingo**: This is similar to number 2 and connected with 0. While using GPT3.5 you need to use the same words used by documentation of the programming language and libraries you use. With GPT4 you can be more lenient.

6. **Avoid coding with Context using new libraries**: Connected with 0. If you do not know the library you will not be able to describe the code you want to write. GPT3.5 will hallucinate. With GPT4 however you can be way more lenient.

7. **Expriment with describing code rather than the effect**: Instead of writing you want to "generate a blue modern navigation bar styling" try to to describe how to write the code "write an id for a navbar, it should be blue, with list elements floating to the left"

## Features/Specification V1 (CURRENT)

### Context Variables

This feature allows users to specify a block of code as a context variable. This context can be used in subsequent prompts.

If a context is declared without a name, it is added as part of the global context for the file and will be used in all subsequent prompts.

**Syntax:**

```python
#<context:ExampleFunction>
# Code block here
#<context:ExampleFunction/>
```

or for global context:

```python
#<context>
# Code block here
#<context/>
```

### Prompts

These can be used much like functions. Context variables can only be used inside prompts.

There can be multiple context variables used. The output can then be used anywhere in the file after the declaration. The output from the prompt can be overwritten or used as context for refinement depending on the use of different tags.

Here are three examples that demonstrate the different use cases:

1. Using output variable with {} syntax: This denotes the use of the generated code in the subsequent lines of the script. The output variable {Functions} can be referenced throughout the code after its declaration. The line containing the output variable will be overwritten with the output of the prompt. The {ExampleFunction} in the prompt is a reference to the context variable specified in feature 1.

    **Syntax:**

    ```python
    #<prompt:Functions>Please write 3 functions for this calculator file. {ExampleFunction}<prompt:Functions/>
    #{Functions}
    ```

2. Using output variable with <> syntax: This denotes that the code block enclosed within the <> tags will be replaced with the generated code each time the tool is run.

    **Syntax:**

    ```python
    #<prompt:NewFunction>Please write a function that squares a number.<prompt:NewFunction/>
    #<NewFunction>
    # Code block here
    #<NewFunction/>
    ```

3. Using output variable with <> syntax and existing code as context: This allows the existing code block to be used as context for the prompt, enabling more nuanced code modification. The existing code block within the <> tags forms part of the context for the prompt and gets replaced with the generated code each time the tool is run.

    **Syntax:**

    ```python
    #<prompt:Code_Piece>Please modify this code to calculate the square of a number. {Code_Piece}<prompt:Code_Piece/>
    #
    #<Code_Piece>
    # Code block here
    #<Code_Piece/>
    ```

    Note: If a prompt does not have any associated output variable used either with {} or <> syntax, the prompt will not run.

## Features/Specification V2 (TO DO)
### Support for shortened aliases
All tags should get a shortened 2 letter version. All closing tags should have "</>" syntax.
Previous syntax will still be supported for compatibility and in case a user wants more readability.
**Syntax:**

```
prompt declaration -            <pr:PromptName></>
context variable declaration -  <cn:VarName></>
file import -                   <fl></>
import context variable -       <im:VarName></>
import all context variables -  <im></>
```


## Features/Specification V3 (TO DO)
### Comment Code Generation

This feature allows users to generate code based on comments. Every block of comments (one or multiple lines without a break line) within the comment_code tags is treated as a separate prompt. Context variables can be referenced in the comments using the {} syntax. The lines below a comment until another comment or the closing tag are replaced by the code generated from the prompt.

**Syntax:**

```python
#<comment_code>
# Function to calculate the sum of two numbers
# Function to calculate the division of two numbers
# Function to return a "Hello World" string
#</comment_code>
```

### Inline Prompts

This feature allows users to place one-off prompts inline within the code. The output from these prompts will overwrite the inline prompt itself, making it a convenient tool for single-use, immediate code generation tasks.

**Syntax:**

```python
#<inline:Please write a function that squares a number.>
```

## Documentation: 
A dedicated site is not yet created.

## Contributing
If you want to contribute, and you know how to run an open source project then please contact me.

## License
[Apache 2.0 License](LICENSE)