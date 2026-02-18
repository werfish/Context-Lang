
// Importing specific context variables
//<import:new1>test_file_1.txt<import:new1/>
//<import:new2>test_file_1.txt<import:new2/>
//<import:new3>test_file_1.txt<import:new3/>
//<import:A>test_file_1.txt<import:A/>
//<import:B>test_file_1.txt<import:B/>

// Importing all context variables from a file
//<import>test_file_2.txt<import/>
//<import>test_file_3.txt<import/>

// Importing another file as a context variable (file context)
//<file:FILE_CONTEXT>test_file_4.txt<file:FILE_CONTEXT/>
//<file:ANOTHER_FILE_CONTEXT>test_file_5.txt<file:ANOTHER_FILE_CONTEXT/>
//<file:CODE1>test_file_6.py<file:CODE1/>
//<file:CODE2>test_file_7.py<file:CODE2/>
//<file:CODE3>test_file_8.py<file:CODE3/>
using System;
namespace ContextTest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Testing extensive imports with Context.");
        }
    }
}
