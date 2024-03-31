
#<context:B>This is context variable B<context:B/>
#<prompt:DuplicateTag>Please write a simple print statement.<prompt:DuplicateTag/>
#<DuplicateTag>
# This is a duplicate tag usage, which should trigger an error
#<DuplicateTag/>

#<DuplicateTag>
#<DuplicateTag/>

#{DuplicateTag}
#{DuplicateTag}
print("Testing duplicate output tags in Python")
