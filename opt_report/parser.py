#! /usr/bin/python3

import re
import sys
from enum import Enum

import intel_compiler.opt_report.regex as regex
from intel_compiler.opt_report.loop_nesting_structure import *

class Parser:

    """ 
    Intel C/C++ Compiler optimization report handle. 
    The main driver, responsible for interaction between all front-end components.    
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
    
    def next_token():
        self.current_token = self.lexer.get_next_token()
    
    def error(expected):
        sys.exit("parser: error")

    def accept(expected):
        return current_token.token_class == expected

    def expect(expected):
        token = self.current_token
        if accept(expected):
            self.next_token()
            return token
        else:
            self.error(expected)

    def skip_loop():
        
        while True:
            token = self.lexer.get_next_token()
            if token.token_class == TokenClass.LOOP_BEGIN:
                self.skip_loop()
            elif token.token_class == TokenClass.LOOP_END:
                break;
            else:
                continue
            
        return            
    
    def parse_optimization_report(loop_nest_struct):
        return parse_loop_report_list(loop_nest_struct)

    def parse_loop_report_list(loop_nest_struct):
    
        while True:
            token = self.lexer.get_next_token()
            
            if token.token_class == TokenClass.EOR:
                break
            
            # Skip all inlined loops in our report;
            # Loop is considered only in its original point of definition;
            if token.token_class == TokenClass.LOOP_BEGIN:
                if token.inlined == True:
                    self.skip_loop()
                    continue
                else:
                    # get Loop object to fill with the information parsed out of loop report
                    loop_name = Loop.form_main_loop_name(loop_filename, loop_line)
                    loop = loop_nest_struct.get_top_level_loop(loop_name)
                    if loop == None:
                        # haven't seen any parts of this loop yet
                        loop_type = LoopType.MAIN
                        num = 0 # number 0 for the main loop part
                        loop = Loop(loop_filename, loop_line, loop_depth, loop_type, num)
                        loop_nest_struct.add_top_level_loop(loop)
                        loop_nest_struct.add_loop(loop)
                
                    # parse loop
                    self.parse_loop(loop)
        
        return True


    def parse_loop_partition_tag(loop, line):

        # swap an object loop pointer points to;
        # main loop component -> peeled loop part;
        # all further ICC remarks in the current report scope
        # relate to a loop peeled part object;

        # provided line matched any of the loop partitioning tags
        match = False

        # check if it is a distributed chunk of the original loop
        re_match = LOOP_DISTR_CHUNK_re.search(line)
        if re_match != None:
            match = True
            num = re_match.group(1)
            distr_chunk_loop = loop.get_distr_chunk(num)
            if distr_chunk_loop == None:
                loop_type = LoopType.DISTRIBUTED_CHUNK
                distr_chunk_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
                loop.add_distr_chunk(distr_chunk_loop, num)
            return (distr_chunk_loop, match) 

        # check if it is a peeled off part of the original loop
        re_match = LOOP_PEEL_re.search(line)
        if re_match != None:
            match = True
            peel_loop = loop.get_peel_loop()
            if peel_loop == None:
                loop_type = LoopType.PEEL
                peel_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, 0)
                loop.add_peel_loop(peel_loop)
            return (peel_loop, match)
 
        # check if it is a loop vectorization remainder
        re_match = LOOP_VECTOR_REMAINDER_re.search(line)
        if re_match != None:
            match = True
            remainder_loop = loop.get_remainder_loop()
            if remainder_loop == None:
                loop_type = LoopType.REMAINDER
                remainder_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, 0)
                loop.add_remainder_loop(remainder_loop)
                return (remainder_loop, match)

        # no loop partitioning tags have been identified, 
        # continue the filling of the main loop
        return (loop, match)

    def parse_loop_remark(loop, line):

        # Checking for different ICC remarks reflecting loop optimization status
        
        # line matched any of the ICC relevant remarks
        match = False

        # Checking loop parallelization remarks
        re_match = LOOP_PARALLEL_re.search(line)
        if re_match != None:
            match = True
            loop.classification.parallel = Classification.YES
            return match

        re_match = LOOP_PARALLEL_POTENTIAL_re.search(line)
        if re_match != None:
            match = True
            loop.classification.parallel_potential = Classification.YES
            return match

        # Checking loop vectorization remarks
        re_match = LOOP_VECTOR_re.search(line)
        if re_match != None:
            match = True
            loop.classification.vector = Classification.YES
            return match

        re_match = LOOP_VECTOR_POTENTIAL_re.search(line)
        if re_match != None:
            match = True
            loop.classification.vector_potential = Classification.YES
            return match

        # Checking loop dependence remarks
        re_match = LOOP_PARALLEL_DEPENCENCE_re.search(line)
        if re_match != None:
            match = True
            loop.classification.parallel_dependence = Classification.YES
            return match

        re_match = LOOP_VECTOR_DEPENCENCE_re.search(line)
        if re_match != None:
            match = True
            loop.classification.vector_dependence = Classification.YES
            return match

        return match

    def parse_loop(loop):
 
        """ 
        Syntactic analysis of Intel C/C++ Compiler optimization report. 
        
        This method examines all ICC remarks of the given loop, and fills LoopClassificationInfo 
        with the relevant information. It calls itself and goes recursively down, if it encounters
        an inner loop in the current loop's optimization report.
        """
        
        loop = original_loop

        line = self.report.readline()
        loop, re_match = parse_loop_partition_tag(loop, line)

        while True:
           
            line = self.report.readline()

            # [1] Checking for any main loop partitioning tags first:
            # * loop distribution optimization
            # * loop vectorization peels
            # * loop vectorization remainders
            
            if loop_partition == 
            loop, re_match = parse_loop_partition_tag(loop, line)
            if re_match == True:
                continue
            elif loop is not original_loop:
                sys.exit("error: unjustified loop partition Loop object pointer substitution!")

            # [2] Checking for different ICC remarks reflecting loop optimization status
            re_match = parse_loop_remark(loop, line)
            if re_match == True:
                continue

            # [3] Checking loop report boundaries (nested inner loop report, loop end mark)
            
            # detected inner loop -> process it recursively
            re_match_loop_begin = regex.LOOP_BEGIN_re.search(line)
            re_match_loop_begin_inlined = regex.LOOP_BEGIN_INLINED_re.search(line)
            if re_match_loop_begin != None and re_match_loop_begin_inlined == None:
                subloop_filename = re_match_loop_begin.group(1)
                subloop_line = re_match_loop_begin.group(2)
                subloop_depth = loop.depth+1
                subloop_name = Loop.form_loop_name(subloop_filename, subloop_line) 
                
                # get inner loop object to fill with optimization information  
                subloop = loop.get_inner_loop(subloop_name)
                if subloop == None:
                    peeled = False
                    remainder = False
                    subloop = Loop(subloop_filename, subloop_line, subloop_depth, peeled, remainder)
                    loop.add_inner_loop(subloop)
                
                # parse inner loop
                self.parse_loop(subloop)
                continue

            # the end of the loop
            re_match_loop_end = LOOP_END_re.search(line)
            if re_match_loop_end != None:
                # we are done with this loop ->
                # -> return to the parent loop processing 
                break

            # fused loops
            fused_loops_match = FUSED_LOOPS_RE.search(line)
            if fused_loops_match != None:
                fused_loops_str = fused_loops_match.group(1)
                fused_loops = [int(s) for s in fused_loops_str.split() if s.isdigit()]
                loop_info.fused = Classification.YES
                loop_info.fused_with = fused_loops
                continue
            fused_loops_match = LOOP_FUSION_LOST_RE.search(line)
            if fused_loops_match != None:
                loop_info.fused_lost = Classification.YES
                continue

            # distributed loop
            distr_loop_match = DISTRIBUTED_LOOP_RE.search(line)
            if fused_loops_match != None:
                fused_loops_str = fused_loops_match.group(1)
                fused_loops = [int(s) for s in fused_loops_str.split() if s.isdigit()]
                loop_info.fused = Classification.YES
                loop_info.fused_with = fused_loops
                continue
            fused_loops_match = LOOP_FUSION_LOST_RE.search(line)
            if fused_loops_match != None:
                loop_info.fused_lost = Classification.YES
                continue

            # no loop optimizations
            loop_no_optimizations_match = LOOP_NO_OPTIMIZATIONS_RE.search(line)
            if loop_no_optimizations_match != None:
                if loop_classification[loop_name] == 3:
                    loop_classification[loop_name] = 0 # non-parallelizible
                continue

        return

loop_classification_table_headers = {}

def print_loop_classification_table_header():
    
    
    
    
    
    report_header = ""
    # Loop parallelisability
    report_header += "loop-name"
    report_header += ":parallel"
    report_header += ":vector"
    report_header += ":parallel-potential"
    report_header += ":vector-potential"
    report_header += ":remainder"
    report_header += ":dependence"
    report_header += ":openmp-pragma"
    # Applied loop optimizations
    # (loop-fusion)
    report_header += ":fused"
    report_header += ":fused-with"
    # (loop-distribution)
    report_header += ":distr"
    report_header += ":distr-n"
    report_header += ":distr-chunk"
    report_header += ":distr-chunk-n"
    # (loop-collapsing)
    report_header += ":collapsed"
    report_header += ":collapsed-with"

    print(report_header)


def print_loop_report(loop_name, loop_inf_record):
    loop_report_str = loop_name + ":"

    if (loop_inf_record.par == True) and (loop_inf_record.vec):
        print(loop_name + ":1")
    elif (classification == 3) or (classification == 2):

    print(loop_report_str)

def print_icc_loop_table_report(loop_classifications):
    print_icc_loop_report_header()
    
    for name, classification in loop_classification.items():


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
