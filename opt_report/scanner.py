#! /usr/bin/python3

import re
import sys
import os

class Scanner:

    """ 
    Intel C/C++ Compiler (ICC) optimization report Scanner.
    """
    
    def __init__(self, lexer=None, report_filename=""):
        
        self.lexer = lexer # lexer reference
        self.report_filename = report_filename
        
        self.lexeme_num = 0

        if not os.path.exists(self.report_filename):
            error_str = "error: "
            error_str += "scanner: "
            error_str += "could not find provided Intel C/C++ Compiler optimization report file (" + str(self.report_filename) + ")"
            sys.exit(error_str)
        self.report = open(self.report_filename, "r")

    def get_next_lexeme(self):
        lexeme = self.report.readline()
        if lexeme != "":
            self.lexeme_num += 1
        return lexeme 
    
    def get_lexeme_num(self):
        return self.lexeme_num

if __name__ == "__main__":
    
    print("= Intel C/C++ Compiler optimization report Scanner =")
    print("Produces a list of lexemes read out of provided optimization report file")

    print("=> intel_compiler.opt_report.scanner DEBUG mode")

    if len(sys.argv) != 2:
        error_str = "error: "
        error_str += "scanner: "
        error_str += "incorrect argument list => use ./scanner opt-report-filename"
        sys.exit(error_str)

    scanner = Scanner(None, sys.argv[1])

    while True:
        lexeme = scanner.get_next_lexeme()
        
        if lexeme != "":
            print(str(scanner.get_lexeme_num()) + ": " + lexeme)
        else:
            break
    
    print("=> intel_compiler.opt_report.scanner DEBUG mode finished!")
    sys.exit()

else:
    pass
