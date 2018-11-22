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
        
        # create in-memory loop nesting structure IR out of ICC opt report 
        if self.parser.parse_optimization_report(self.ir) == True:
            pass
        else:
            sys.exit("error: compiler: could not compile the input file")
        
        src_loops = self.ir.get_loops()
        fused_loops = self.ir.get_fused_loops()
        collapsed_loops = self.ir.get_collapsed_loops()

        # loop fusion post-processing
        for loop in fused_loops:
            if loop.classification.fused == Classification.YES:
                # exclude itself
                fused_with = loop.classification.fused_with[1:]
                for fused_loop_line in fused_with:
                    name = loop.form_main_loop_name(loop.filename, fused_loop_line)
                    fused_loop = src_loops[name]
                    fused_loop.classification.copy(loop.classification)
            else:
                sys.exit("error: compiler: fused_loops list misformation")

        # loop collapsing post-processing
        for loop in collapsed_loops:
            if loop.classification.collapsed == Classification.YES:
                # exclude itself
                collapsed_with_line = loop.classification.collapsed_with
                name = loop.form_main_loop_name(loop.filename, collapsed_with_line)
                collapsed_loop = src_loops[name]
                collapsed_loop.classification.copy(loop.classification)
            else:
                sys.exit("error: compiler: fused_loops list misformation")

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
