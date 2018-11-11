#! /usr/bin/python3

import sys

from opt_report_compiler.lexer import Lexer
from opt_report_compiler.parser import Parser
from opt_report_compiler.ir import *

class IccOptReportCompiler:

    """ 
    Intel C/C++ Compiler (ICC) optimization report compiler.
    The main driver class, responsible for interaction between all compiler components.    
    """

    def __init__(self, report_filename):
        self.report_filename
        self.lexer = Lexer(self.report_filename)
        self.parser = Parser(self.lexer)
        self.ir = LoopNestingStructure()

    def compilation_error():
        error_str = "IccOptReportCompiler(): optimization report compilation error: "
        error_str += "could not compile " + str(self.report_filename)
        sys.exit("[!] error: " + error_str)

    def get_ir():
        return self.ir

    def compile():
        if self.parser.parse_optimization_report(self.ir) == True:
            pass
        else:
            compilation_error()        

if __name__ == "__main__":
    print("Intel C/C++ Compiler (ICC) optimization report compiler has been defined")
else:
    pass
