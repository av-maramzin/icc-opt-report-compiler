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

    def print_compilation_report(self):
        
        src_loops = self.ir.get_loops()
        fused_loops = self.ir.get_fused_loops()
        collapsed_loops = self.ir.get_collapsed_loops()

        print("ICC optimization report " + self.report_filename + " has been successfully compiled!")
        print("loops total: " + str(len(src_loops)))
        print("loop fusions: " + str(len(fused_loops)))
        print("loop collapsings: " + str(len(collapsed_loops)))

        num = 1
        for loop_name, loop in src_loops.items():
            
            print("loop [" + str(num) + "]: " + loop_name)
            print("{")
            print("\tdepth: " + str(loop.depth))
            print("\n")
             
            loop_class = loop.classification
            
            print("\tparallel: " + loop_class.parallel.name)
            print("\tparallel potential: " + loop_class.parallel_potential.name)
            print("\tvector: " + loop_class.vector.name)
            print("\tvector potential: " + loop_class.vector_potential.name)
            print("\tparallel dependence: " + loop_class.parallel_dependence.name)
            print("\tvector dependence: " + loop_class.vector_dependence.name)
            print("\tno optimizations: " + loop_class.no_opts.name)
            print("\topenmp: " + loop_class.openmp.name)
            print("\ttiled: " + loop_class.tiled.name)
            print("\tfused: " + loop_class.fused.name)
            print("\tfused with:" + ', '.join(str(line) for line in loop_class.fused_with))
            print("\tlost in fusion: " + loop_class.fused_lost.name)
            print("\tdistributed: " + loop_class.distr.name)
            print("\tdistributed-num: " + str(loop_class.distr_parts_n))
            print("\tcollapsed: " + loop_class.collapsed.name)
            print("\tcollapsed with: " + str(loop_class.collapsed_with))
            print("\tcollapse eliminated: " + loop_class.collapse_eliminated.name)
            print("\n")

            print("\tinner loops:")
            inner_num = 1
            for inner_loop_name, inner_loop in loop.inner_loops.items():
                print("\t\tloop [" + str(inner_num) + "]: " + loop_name)
                inner_num += 1
            print("\n")
 
            print("\tdistributed chunks:")
            for distr_chunk_num, distr_chunk in loop.distr_chunks.items():
                print("\t\tdistr chunk [" + str(distr_chunk_num) + "]: " + str(distr_chunk))

            print("}")
            print("\n")
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
