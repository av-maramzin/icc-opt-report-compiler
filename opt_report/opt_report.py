#! /usr/bin/python3

import sys

from opt_report_compiler.lexer import Lexer
from opt_report_compiler.parser import Parser
from opt_report_compiler.ir import *

class IccOptReport:

    """ 
    Intel C/C++ Compiler optimization report handle. 
    The main driver, responsible for interaction between all front-end components.    
    """

    def __init__(self, report_filename):
        self.lexer = Lexer(report_filename)
        self.parser = Parser(self.lexer)

    def process():
       
        # prepare optimization report intermediate representation (IR) object  
        loop_nest_struct = LoopNestingStructure()
        
        self.parser.parse_optimization_report(loop_nest_struct)
        

if __name__ == "__main__":

    print("<= Intel C/C++ Compiler optimization report processing script =>")

    if len(sys.argv) != 3:
        error_str = "script usage error: use ./transform-icc-opt-report.py (icc_report_file) (approximation_num)\n"
        error_str += "where (icc_report_file) is the optimization report file produced by ICC compiler,\n"
        error_str += "and (approximation_num) is the level of detail to capture in the ICC report\n"
        sys.exit("error: " + error_str)

    icc_opt_report_filename = sys.argv[1]
    icc_opt_report = IccOptReport(icc_opt_report_filename)

    
    report_detail_level = int(sys.argv[2]) # the greater the level, the more precise report is
    if report_detail_level not in [1,2,3]:
        error_str = "the loop classification table detail level (detail-level) must be in [1,3] range!"
        sys.exit("error: " + error_str)

    icc_report_file = open(sys.argv[1],"r")
    
    loop_class_table = LoopClassificationTable(report_detail_level)
    loop_depth = 0
   
    # read ICC optimization report file line by line, recursively build 
    # corresponding loop nesting structure and populate it with optimization
    # information out of ICC compiler report
    while True:
        line = icc_report_file.readline()
        if line == "":
            break
        loop_begin_match = LOOP_BEGIN_RE.search(line)
        if loop_begin_match != None:
            loop_filename = loop_begin_match.group(1)
            loop_line = loop_begin_match.group(2)
            loop_name = loop_filename + "(" + loop_line + ")"
            if loop_name not in loop_classification:
                loop_classification[loop_name] = LoopInformationRecord(loop_name, loop_filename, int(loop_line))
                extract_loop_information(loop_name, loop_classification[loop_name])
        else:
            openmp_construct_match = OPENMP_CONSTRUCT_RE.search(line)
            if openmp_construct_match != None:
                loop_name = openmp_construct_match.group(1) + "(" + openmp_construct_match.group(2) + ")"
                line = icc_report_file.readline()
                openmp_parallel_match = OPENMP_PARALLEL_RE.search(line)
                if openmp_parallel_match != None:
                    if loop_name not in loop_classification:
                        loop_classification[loop_name] = 1 # OpenMP parallelized
                    else:
                        if loop_classification[loop_name] == 3 or loop_classification[loop_name] == 0:
                            loop_classification[loop_name] = 1 # OpenMP parallelized

    print_icc_loop_report(loop_classification)
    for name, classification in loop_classification.items():
        

    print("Done!")
