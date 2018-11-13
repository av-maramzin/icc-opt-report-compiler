#! /usr/bin/python3

import re
import sys
from enum import Enum

import icc_opt_report_regex

class Classification(Enum):
    NO = 0
    YES = 1
    UNSTATED = 2
    UNINITIALIZED = 3

class LoopType(Enum):
    MAIN = 0
    DISTRIBUTED_CHUNK = 1
    PEEL = 2
    VECTOR_REMAINDER = 3
    REMAINDER = 4
    UNKNOWN = 5

class LoopClassificationInfo:
    
    """ All the information derived out of Intel C/C++ Compiler report """
    
    def __init__(self, loop):
        
        # pointer to the loop object this classification applies to
        self.loop = loop

        # loop's parallelisation status
        self.parallel = Classification.UNINITIALIZED
        # loop could potentially be parallelized, but wasn't
        self.parallel_potential = Classification.UNINITIALIZED

        # loop vectorization status
        self.vector = Classification.UNINITIALIZED
        # loop could potentially be vectorized, but wasn't
        # (inner loop was targeted for vectorization, for example)
        self.vector_potential = Classification.UNINITIALIZED

        # loop dependence present
        self.parallel_dependence = Classification.UNINITIALIZED
        self.vector_dependence = Classification.UNINITIALIZED

        # #pragma omp presence
        self.openmp = Classification.UNINITIALIZED
       
        # loop fusion
        self.fused = Classification.UNINITIALIZED
        self.fused_with = []
        self.fused_lost = Classification.UNINITIALIZED
        # loop fission (distribution)
        self.distributed = Classification.UNINITIALIZED
        self.distr_parts_n = 0
        # loop collapsing
        self.collapsed = Classification.UNINITIALIZED
        self.collapsed_with = []
        self.collapsed_eliminated = Classification.UNINITIALIZED

class Loop:

    """ Loop, as found in the source code """

    def form_main_loop_name(filename="", line=-1):
        return filename + "(" + str(line) + ")"

    def __init__(self, filename="", line=-1, depth=-1, loop_type=LoopType.UNKNOWN, number=-1):

        # reference to a LoopNestingStructure this loop belongs to
        self.loop_nest_struct = None

        # pointers linking loop objects into a whole consistent loop nesting structure
        # parent of an inner loop
        self.parent = None
        # main loop reference for distributed parts of a loop, remainders, peels, etc.
        self.main = None

        # loop's location on the host filesystem, depth, type, etc.
        self.filename = filename
        self.line = line
        self.depth = depth
        self.loop_type = loop_type
        self.number = number

        if loop_type == LoopType.MAIN:
            self.name = filename + "(" + line + ")"
        elif loop_type == LoopType.DISTRIBUTED_CHUNK:
            self.name = filename + "(" + str(line) + ")" + "-" + str(number)
        elif loop_type == LoopType.PEEL:
            self.name = filename + "(" + str(line) + ")" + "/"
        elif loop_type == LoopType.VECTOR_REMAINDER:
            self.name = filename + "(" + line + ")v%"
        elif loop_type == LoopType.REMAINDER:
            self.name = filename + "(" + line + ")%"
        elif loop_type == LoopType.UNKNOWN:
            sys.exit("A type of the loop " + filename + "(" + str(line) + ")" + "has not been specified")
        
        # loop's composition
        self.inner_loops = {}
        self.distr_chunks = {}
        self.vector_remainder = None
        self.remainder = None
        self.peel = None
        
        # all loop optimization information gathered from ICC report
        self.classification = LoopClassificationInfo(self)
   
    def get_parent_loop():
        return self.parent

    def set_parent_loop(parent):
        self.parent = parent

    def get_main_loop():
        return self.main

    def set_main_loop(main):
        self.main = main

    def get_inner_loop(inner_loop_name):
        if inner_loop_name in self.inner_loops:
            return self.inner_loops[inner_loop_name]
        else:
            return None

    def add_inner_loop(inner_loop):
        if inner_loop.name not in self.inner_loops:
            if inner_loop.name not in self.loop_nest_struct.loops:
                inner_loop.set_parent_loop(self)
                self.inner_loops[inner_loop.name] = inner_loop
                self.loop_nest_struct.loops[inner_loop.name] = inner_loop
                return True
            else:
                sys.exit("loop nesting structure inconsistency: loop.inner_loops vs loop.loop_nest_struct.loops")
        else:
            if inner_loop.name in self.loop_nest_struct.loops:
                return False
            else:
                sys.exit("loop nesting structure inconsistency: loop.inner_loops vs loop.loop_nest_struct.loops")

    def get_distr_chunk(num):
        if num in self.distr_chunks:
            return self.distr_chunks[num]
        else:
            return None 

    def add_distr_chunk(distr_chunk, num):
        if num not in self.distr_chunks:
            distr_chunk.set_main_loop(self)
            self.distr_chunks[num] = distr_chunk
            return True
        else:
            return False

    def get_peel_loop():
        return self.peel

    def add_peel_loop(peel_loop):
        if self.peel == None:
            peel_loop.set_main_loop(self)
            self.peel = peel_loop
            return True
        else:
            return False

    def get_remainder_loop():
        return self.remainder

    def add_remainder_loop(remainder_loop):
        if self.remainder == None:
            remainder_loop.set_main_loop(self)
            self.remainder = remainder_loop
            return True
        else:
            return False

class LoopNestingStructure:

    """ Loop Table All the information derived out of Intel C/C++ Compiler report """

    def __init__(self):
        # dictionary of all original (top-level and nested) loops 
        self.top_level_loops = {}
        # dictionary of all original (top-level and nested) loops 
        self.loops = {}
 
    def get_top_level_loop(loop_name):
        if loop_name in self.top_level_loops:
            return self.top_level_loops[loop_name]
        else:
            return None
   
    def add_top_level_loop(loop):
        if loop.name not in self.top_level_loops:
            if loop.name not in self.loops:
                loop.loop_nest_structure = self
                self.top_level_loops[loop.name] = loop
                self.loops[loop.name] = loop
                return True
            else:
                sys.exit("loop nesting structure inconsistency: self.top_level_loops vs self.loops")
        else:
            if loop.name not in self.loops:
                return False
            else:
                sys.exit("loop nesting structure inconsistency: self.top_level_loops vs self.loops")

    def get_loop(loop_name):
        if loop_name in self.loops:
            return self.loops[loop_name]
        else:
            return None

if __name__ == "__main__":
    print("Done!")
else:
    pass
