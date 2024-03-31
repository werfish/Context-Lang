//<file:CODE3>test_file_8.py<file:CODE3/>
//<import:new1>test_file_1.txt<import:new1/>
//<file:CODE2>test_file_7.py<file:CODE2/>
//<import:new3>test_file_1.txt<import:new3/>
//<import>test_file_3.txt<import/>
//<import:new2>test_file_1.txt<import:new2/>
//<import:A>test_file_1.txt<import:A/>
//<import>test_file_2.txt<import/>
//<file:ANOTHER_FILE_CONTEXT>test_file_5.txt<file:ANOTHER_FILE_CONTEXT/>

using System;
namespace ContextTest//<import:B>test_file_1.txt<import:B/>
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Testing extensive imports with Context."); //<file:CODE1>test_file_6.py<file:CODE1/>
        }
    } //<file:FILE_CONTEXT>test_file_4.txt<file:FILE_CONTEXT/>
}
