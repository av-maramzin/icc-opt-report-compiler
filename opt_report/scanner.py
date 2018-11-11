#! /usr/bin/python3

import re
import sys

class Scanner:

    """ 
    Intel C/C++ Compiler (ICC) optimization report scanner 
    """
    
    def __init__(self, lexer=None, report_filename=""):
        self.lexer = lexer # lexer reference
        self.report_filename = report_filename
        if not os.path.exists(self.report_filename):
            error_str = "scanner error: could not find Intel C/C++ Compiler optimization report file (" + str(self.report_filename) + ")"
            sys.exit(error_str)
        self.report = open(self.report_filename, "r")

    def get_next_lexeme():
        return self.report.readline()

if __name__ == "__main__":
    print("Done!")
else:
    pass
