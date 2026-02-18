## Roadmap

### Development

1. **Codebase Development**: Currently, Context is just a Proof-of-Concept (POC) written with minimal effort. The lightweight nature and lack of dependencies are benefits, but as the project grows in complexity, it will require several subtasks related to project and development dependencies. These include:
    - Integrate Pre-Commit DONE
    - Integrate Linters, Formatters, etc. DONE
    - Integrate Pytest/Coverage. Develop a strategy for testing cognitive features (for example, running and checking prompts?)
    - Integrate a make file compatible with both Windows and Linux.
    - Another option is to use Poetry wchich I am currently looking into. DONE
    - Implement CI/CD to test features in different environments.
    - Rewrite the parser and language grammar in textX for allowing easy extending of the language
    - Migrate from setup.py to pyproject.toml approach DONE
    - Use langchain for all the functionality

2. **Development Documentation**: Create a document detailing how to run the project for development.

3. **Context CLI Tool Spec**: Create a specification/features section for the Context CLI tool.

4. **Cross-Platform Compatibility**: Ensure all features work on Windows and Linux.

5. **Refactoring**: Refactor the tool to allow for ease of adding more features.

### Context Features

0. **PRIORITY**: Models should be chosen via configuration. Currently it is hardcoded or passed in the commandline. Currently only 2 open AI models are supported.

1. **Bug Fixing**: The priority is to fix any bugs in the Context preprocessor and code generation for V1 Spec of ContextLang.

2. **Platform Compatibility**: Ensure Context works on all platforms.

3. **Code Generation Improvement**: The code generation process is not perfect. The prompts need to be rewritten from the initial POC version to be more precise and robust.

4. **Caching Mechanism**: Add a JSON caching mechanism to Context so it only runs prompts that have been modified since the previous run. Add a CLI option --RunAll for running all prompts.

5. **No New Features Before Bug Fixing**: No new features should be added before points 1, 2, 3, and 4 are achieved.

6. **.context_ignore Feature**: Add a .context_ignore feature, which would work like .gitignore but for Context.

7. **Asynchronous Processing**: Add async processing for each AST tree.

8. **Custom Prompts**: Add an option so a user can add their own prompts to the code generation process. (basically creating workflows).

### ContextLang Features

- **Separate Files**: Conceptualize and add a feature for using ContextLang in separate .ctxt files, which allow a simpler syntax and enable building a file from prompts declared in .ctxt. This is still in the concept stage.
- **HEAD, TAIL, and MID Functions**: Add HEAD, TAIL, and MID functions to file imports in some version of the spec. This is also still in the concept stage.
- **Streamlint frontend allowing chatting with the code base**: After running Context Analyze user should see a streamlit frontend allowing chatting with the codebase. (RESEARCHING THIS IN PROGRES, Frontend done, currently fixing bugs)

If you have any ideas to extend the functionality, please contact me.
