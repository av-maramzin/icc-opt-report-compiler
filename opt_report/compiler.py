#! /usr/bin/python3

import sys
import logging

from lexer import Lexer
from parser import Parser
from ir import *

class IccOptReportCompiler:

    """ 
    Intel C/C++ Compiler (ICC) optimization report compiler.
    The main driver class, responsible for interaction between all compiler components.    
    """
    
    def __init__(self, report_filename):
        self.report_filename = report_filename
        self.lexer = Lexer(self.report_filename)
        self.parser = Parser(self.lexer)
        self.ir = LoopNestingStructure()

    def get_ir(self):
        return self.ir

    def compile(self):
        if self.parser.parse_optimization_report(self.ir) == True:
            pass
        else:
            sys.exit("error: compiler: could not compile the input file")

if __name__ == "__main__":

    print("= Intel C/C++ Compiler (ICC) optimization report compiler =")
    print("Compiler: ICC opt report file -> Lexer -> a list of tokens ->\n")
    print("-> Parser -> in-memory IR\n")

    print("=> icc.opt_report.compiler DEBUG mode\n")

    logging.basicConfig(filename='compiler.debug', level=logging.DEBUG)

    logging.debug('Debugging compiler.py')

    if len(sys.argv) != 2:
        error_str = "error: "
        error_str += "compiler: "
        error_str += "incorrect argument list => use ./compiler.py opt-report-filename"
        sys.exit(error_str)

    compiler = IccOptReportCompiler(sys.argv[1])
    compiler.compile()

    print("=> icc.opt_report.compiler DEBUG mode finished!")
    
    sys.exit()

else:
    pass
