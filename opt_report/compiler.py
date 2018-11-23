#! /usr/bin/python3

import sys
import logging

import numpy as np
import matplotlib.pyplot as plt

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

    def print_compilation_report(self):
        
        src_loops = self.ir.get_loops()
        fused_loops = self.ir.get_fused_loops()
        collapsed_loops = self.ir.get_collapsed_loops()

        print("ICC optimization report " + self.report_filename + " has been successfully compiled!\n")

        print("===== Overall statistics =====")
        print("\n", end="")
        
        print("loops total: " + str(len(src_loops)))
        print("\n", end="")
        
        print("= Optimizations =")
        print("\n", end="")

        print("loop fusions: " + str(len(fused_loops)))
        print("loop collapses: " + str(len(collapsed_loops)))

        distr_loop_num = 0
        parallel_loop_num = 0
        vector_loop_num = 0
        parallel_dep_num = 0
        vector_dep_num = 0
      
        loop_depth_hist = {}

        for loop_name, loop in src_loops.items():
            
            if loop.depth not in loop_depth_hist:
                loop_depth_hist[loop.depth] = 1
            else:
                loop_depth_hist[loop.depth] += 1

            if len(loop.distr_chunks) != 0:
                distr_loop_num += 1
            
            if loop.classification.parallel == Classification.YES:
                parallel_loop_num += 1
 
            if loop.classification.vector == Classification.YES:
                vector_loop_num += 1

            if loop.classification.parallel_dependence == Classification.YES:
                parallel_dep_num += 1

            if loop.classification.vector_dependence == Classification.YES:
                vector_dep_num += 1
      
        print("loop distributions: " + str(distr_loop_num))
        print("\n", end="")

        print("= Classifications =")
        print("\n", end="")

        print("parallel loops: " + str(parallel_loop_num))
        print("vector loops: " + str(vector_loop_num))
        print("parallel dependence: " + str(parallel_dep_num))
        print("vector dependence: " + str(vector_dep_num))
        print("\n", end="")

        print("===== ================== =====")

        width = 0.5
        plt.bar(loop_depth_hist.keys(), loop_depth_hist.values(), width, color='g')
        plt.show()

        num = 1
        for loop_name, loop in src_loops.items():
            
            print("loop [" + str(num) + "]: (depth: " + str(loop.depth) + ") " + loop_name)
            print("{")
            loop_class = loop.classification
            loop_class.print("\t") 
            print("\n", end="")

            print("\tinner loops:")
            inner_num = 1
            for inner_loop_name, inner_loop in loop.inner_loops.items():
                print("\t\t [" + str(inner_num) + "]: " + "(depth: " + str(loop.depth+1) + ") " + inner_loop_name)
                inner_num += 1
            print("\n", end="")
 
            print("\tdistr chunks:")
            for distr_chunk_num, distr_chunk in loop.distr_chunks.items():
                print("\t\t[" + str(distr_chunk_num) + "]: " + distr_chunk.name + "-" + str(distr_chunk_num))

            print("}")
            print("\n", end="")
            num += 1

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
        for fused_loop_name in fused_loops:
            loop = fused_loops[fused_loop_name]
            if loop.classification.fused == Classification.YES:
                # exclude itself
                fused_with = loop.classification.fused_with[1:]
                for fused_loop_line in fused_with:
                    name = Loop.form_main_loop_name(loop.filename, fused_loop_line)
                    fused_loop = src_loops[name]
                    fused_loop.classification.copy(loop.classification)
            else:
                sys.exit("error: compiler: fused_loops list misformation")

        # loop collapsing post-processing
        for collapsed_loop_name in collapsed_loops:
            loop = collapsed_loops[collapsed_loop_name]
            if loop.classification.collapsed == Classification.YES:
                # exclude itself
                collapsed_with_line = loop.classification.collapsed_with
                name = Loop.form_main_loop_name(loop.filename, collapsed_with_line)
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
    
    compiler.print_compilation_report()

    print("=> icc.opt_report.compiler DEBUG mode finished!")
    
    sys.exit()

else:
    pass
