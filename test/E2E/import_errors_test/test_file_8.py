
# Testing for a potential naming conflict between a prompt, prompt output tag, and a context variable
#<prompt:DuplicateTag>This is a test prompt named DuplicateTag<prompt:DuplicateTag/>
#<DuplicateTag>
# This should serve as a prompt output tag, potentially causing a naming conflict
#<DuplicateTag/>
#<context:DuplicateTag>This is a context variable named DuplicateTag<context:DuplicateTag/>
