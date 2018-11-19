#! /usr/bin/python3

import re
import sys
import logging
from enum import Enum

class Classification(Enum):
    NO = 0
    YES = 1
    UNSTATED = 2
    UNINITIALIZED = 3

class LoopType(Enum):
    MAIN = 0 # main loop's kernel
    DISTR = 1 # distributed chunk
    FUSED = 2 # fused loop
    PEEL = 3 # peeled off loop part
    VECTOR_REMAINDER = 4 # vectorization remainder
    REMAINDER = 5
    LOST = 6
    PARTIAL = 7
    OUTER = 8
    UNKNOWN = 9

class LoopClassificationInfo:
    
    """ All the information derived out of Intel C/C++ Compiler report """
    
    def __init__(self, loop):
        
        # pointer to the loop object this classification applies to
        self.loop = loop

        # loop's parallelisation status
        self.parallel = Classification.UNINITIALIZED
        self.parallel_potential = Classification.UNINITIALIZED

        # loop vectorization status
        self.vector = Classification.UNINITIALIZED
        self.vector_potential = Classification.UNINITIALIZED

        # loop dependence present
        self.parallel_dependence = Classification.UNINITIALIZED
        self.vector_dependence = Classification.UNINITIALIZED

        # #pragma omp presence
        self.openmp = Classification.UNINITIALIZED
       
        # loop collapsing
        self.tiling = 0
        self.tiling_count = 0

        # loop fusion
        self.fused = Classification.UNINITIALIZED
        self.fused_with = []
        self.fused_lost = Classification.UNINITIALIZED
        # loop fission (distribution)
        self.distr = Classification.UNINITIALIZED
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

        # references linking loop objects into a whole consistent loop nesting structure
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

        if self.loop_type.value == LoopType.MAIN.value:
            self.name = filename + "(" + line + ")"
        elif self.loop_type.value == LoopType.FUSED.value:
            self.name = filename + "(" + line + ")"
        elif self.loop_type.value == LoopType.DISTR.value:
            self.name = filename + "(" + str(line) + ")" + "-" + str(number)
        elif self.loop_type.value == LoopType.PEEL.value:
            self.name = filename + "(" + str(line) + ")" + "/"
        elif self.loop_type.value == LoopType.VECTOR_REMAINDER.value:
            self.name = filename + "(" + line + ")v%"
        elif self.loop_type.value == LoopType.REMAINDER.value:
            self.name = filename + "(" + line + ")%"
        elif self.loop_type.value == LoopType.UNKNOWN.value:
            sys.exit("A type of the loop " + filename + "(" + str(line) + ")" + "has not been specified")
        
        # loop's composition
        self.inner_loops = {}
        self.distr_chunks = {}
        self.vector_remainder = None
        self.remainder = None
        self.peel = None
        
        # all loop optimization information gathered from ICC report
        self.classification = LoopClassificationInfo(self)
        
        logging.debug('Loop: => new Loop() obj at ' + str(self))
        logging.debug('Loop: ' + self.filename + '(' + str(self.line) + '): ' + 'depth(' + str(self.depth) + ') ' + self.loop_type.name)

    def get_loop_nest_struct(self):
        return self.loop_nest_struct

    def set_loop_nest_struct(self, loop_nest_struct):
        self.loop_nest_struct = loop_nest_struct

    def get_parent_loop(self):
        return self.parent

    def set_parent_loop(self, parent):
        self.parent = parent

    def get_main_loop(self):
        return self.main

    def set_main_loop(self, main):
        self.main = main

    def get_inner_loop(self, inner_loop_name):
        if inner_loop_name in self.inner_loops:
            return self.inner_loops[inner_loop_name]
        else:
            return None

    def add_inner_loop(self, inner_loop):
        if inner_loop.name not in self.inner_loops:
            inner_loop.set_parent_loop(self)
            self.inner_loops[inner_loop.name] = inner_loop
        
            logging.debug('Loop: => Loop(' + str(self) + ') added a new inner loop Loop(' + str(inner_loop) + ')')
            logging.debug('Loop: loop at ' + self.filename + '(' + str(self.line) + ')')
            logging.debug('Loop: inner loop at ' + inner_loop.filename + '(' + str(inner_loop.line) + ')')

            return True
        else:
            return False

    def get_distr_chunk(self, num):
        if num in self.distr_chunks:
            return self.distr_chunks[num]
        else:
            return None 

    def add_distr_chunk(self, distr_chunk, num):
        if num not in self.distr_chunks:
            distr_chunk.set_main_loop(self)
            self.distr_chunks[num] = distr_chunk

            logging.debug('Loop: => Loop(' + str(self) + ') added a new distributed chunk Loop(' + str(distr_chunk) + ')')
            logging.debug('Loop: loop at ' + self.filename + '(' + str(self.line) + ')')
            logging.debug('Loop: distr loop at ' + distr_chunk.filename + '(' + str(distr_chunk.line) + ')')

            return True
        else:
            return False

    def get_peel_loop(self):
        return self.peel

    def add_peel_loop(self, peel_loop):
        if self.peel == None:
            peel_loop.set_main_loop(self)
            self.peel = peel_loop

            logging.debug('Loop: => Loop(' + str(self) + '): added peel loop Loop(' + str(peel_loop) + ')')
            logging.debug('Loop: loop at ' + self.filename + '(' + str(self.line) + ')')
            logging.debug('Loop: peel loop at ' + peel_loop.filename + '(' + str(peel_loop.line) + ')')

            return True
        else:
            return False

    def get_remainder_loop(self):
        return self.remainder

    def add_remainder_loop(self, remainder_loop):
        if self.remainder == None:
            remainder_loop.set_main_loop(self)
            self.remainder = remainder_loop

            logging.debug('Loop: => Loop(' + str(self) + '): added remainder loop Loop(' + str(remainder_loop) + ')')
            logging.debug('Loop: loop at ' + self.filename + '(' + str(self.line) + ')')
            logging.debug('Loop: remainder loop at ' + remainder_loop.filename + '(' + str(remainder_loop.line) + ')')

            return True
        else:
            return False

    def get_vector_remainder_loop(self):
        return self.vector_remainder

    def add_vector_remainder_loop(self, remainder_loop):
        if self.vector_remainder == None:
            remainder_loop.set_main_loop(self)
            self.vector_remainder = remainder_loop

            logging.debug('Loop: => Loop(' + str(self) + '): added vector remainder loop Loop(' + str(remainder_loop) + ')')
            logging.debug('Loop: loop at ' + self.filename + '(' + str(self.line) + ')')
            logging.debug('Loop: vector remainder loop at ' + remainder_loop.filename + '(' + str(remainder_loop.line) + ')')

            return True
        else:
            return False

class LoopNestingStructure:

    """ 
    class LoopNestingStructure;

    A container for all loops encountered in the Intel C/C++ 
    compiler optimization report. This container stores only 
    references to the original loops (present in the source code,
    and not created by the ICC compiler itself (such as loop
    peels, remainders, distributed parts, etc.)).
    """

    def __init__(self):
        """ LoopNestingStructure constructor method. """   
        
        # dictionary of all original top-level loops, representing 
        # entrance points into the loop nesting structure
        self.top_level_loops = {}

        # convenience data-structure
        # dictionary of all original (not created by the ICC compiler) (top-level and nested) loops;
        # this list is also being populated indirectly out of Loop class objects, through a reference
        # to a LoopNestingStructure class containing the loop
        self.loops = {}
 
    def get_top_level_loop(self, loop_name):
        if loop_name in self.top_level_loops:
            return self.top_level_loops[loop_name]
        else:
            return None
   
    def add_top_level_loop(self, loop):
        if loop.name not in self.top_level_loops:
            self.top_level_loops[loop.name] = loop

            logging.debug('LoopNestStruct: => added a new top level loop Loop(' + str(loop) + ')')
            logging.debug('LoopNestStruct: loop at ' + loop.filename + '(' + str(loop.line) + ')')

            return True
        else:
            return False

    def get_loop(self, loop_name):
        if loop_name in self.loops:
            return self.loops[loop_name]
        else:
            return None
    
    def add_loop(self, loop):
        if loop.name not in self.loops:
            self.loops[loop.name] = loop

            logging.debug('LoopNestStruct: => LoopNestStructure(' + str(self) + ') added a new loop Loop(' + str(loop) + ')')
            logging.debug('LoopNestStruct: loop at ' + loop.filename + '(' + str(loop.line) + ')')

            return True
        else:
            return False

if __name__ == "__main__":
    print("Done!")
else:
    pass
