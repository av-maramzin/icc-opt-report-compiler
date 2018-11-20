#! /usr/bin/python3

import re
import sys
import logging
from enum import Enum

from ir import *
from lexer import Lexer
from tokeniser import *

class Parser:

    """ 
    Intel C/C++ Compiler optimization report handle. 
    The main driver, responsible for interaction between all front-end components.    
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.loop_nest_struct = None

    def skip_loop(self):
        
        while True:
            token = self.lexer.get_next_token()
            if token.token_class == TokenClass.LOOP_END:
                break
            elif token.token_class == TokenClass.LOOP_BEGIN:
                self.skip_loop()
            else:
                continue
            
        return  

    def parse_optimization_report(self, loop_nest_struct):
        logging.debug('Parser: Parser: ===> parse_optimization_report()')
        self.loop_nest_struct = loop_nest_struct
        return self.parse_loop_report_list()

    def parse_loop_report_list(self):
        
        logging.debug('Parser: ===> parse_loop_report_list()')
    
        while True:

            token = self.lexer.get_next_token()
            token_num = '[' + str(self.lexer.get_token_num()) + ']'
           
            # loop report list must start with LOOP BEGIN
            if token.token_class == TokenClass.SKIP:
                logging.debug('Parser: => token ' + token_num + ': skip')
                continue
            elif token.token_class == TokenClass.LOOP_BEGIN:
                # Skip all inlined loops in our report;
                # Loop is considered only in its original point of definition;
                logging.debug('Parser: => token ' + token_num + ': LOOP BEGIN at ' + token.filename + '(' + str(token.line) + ')')
                if token.inlined == True:
                    logging.debug('Parser: skipping inlined loop')
                    self.skip_loop()
                    continue
                else:
                    # get Loop object to fill with the information parsed out of loop report
                    loop_name = Loop.form_main_loop_name(token.filename, token.line)
                    
                    # check if we have ever encountered this loop before (even in inner scopes of previous loops);
                    # sometimes ICC interchanges scopes of loops
                    loop = self.loop_nest_struct.get_loop(loop_name)
                    if loop == None:
                        # haven't seen any parts of this loop yet
                        loop_type = LoopType.MAIN
                        num = 0
                        loop_depth = 0
                        
                        loop = Loop(token.filename, token.line, loop_depth, loop_type, num)
                         
                        if self.loop_nest_struct.add_top_level_loop(loop) == False:
                            sys.exit("error: ir: could not add Loop obj " + str(loop) + " " + token.filename + "(" + str(token.line) + ")" + " to LoopNestingStructure IR.top_level_loops")
                        if self.loop_nest_struct.add_loop(loop) == False:
                            sys.exit("error: ir: could not add Loop obj " + str(loop) + " " + token.filename + "(" + str(token.line) + ")" + " to LoopNestingStructure IR.loops")
                        loop.set_loop_nest_struct(self.loop_nest_struct)
                    elif self.loop_nest_struct.get_top_level_loop(loop_name) == None:
                        if self.loop_nest_struct.add_top_level_loop(loop) == False:
                            sys.exit("error: ir: could not add Loop obj " + str(loop) + " " + token.filename + "(" + str(token.line) + ")" + " to LoopNestingStructure IR.top_level_loops")
                        
                    # parse loop
                    self.parse_loop_report(loop)
            elif token.token_class == TokenClass.EOR:
                break
            else:
                sys.exit("error: parser: got " + token.token_class.name + ", when SKIP or LOOP BEGIN tokens are expected")
       
        return True

    def parse_loop_report(self, outer_main_loop):
       
        # information to be parsed relates to the main outer loop
        loop = outer_main_loop
        if loop == None:
            sys.exit("error: parser: parse_loop_report(): called with None Loop object")
       
        logging.debug('Parser: ===> parse_loop_report(loop=' + str(loop) + ')')
        logging.debug('Parser: Parser: loop at ' + loop.filename + '(' + str(loop.line) + ')')
        
        while True:
            
            token = self.lexer.get_next_token()
            token_num = '[' + str(self.lexer.get_token_num()) + ']'

            if token.token_class == TokenClass.SKIP:
                # this token type is the most frequent ->
                # -> so it is code performance wise to have it 
                # going first in the compound if statement
                logging.debug('Parser: => token ' + token_num + ': skip')
                continue
            elif token.token_class == TokenClass.LOOP_REMARK:
                logging.debug('Parser: => token: ' + token_num + ' loop remark')
                self.parse_loop_remark(loop, token)
                continue
            elif token.token_class == TokenClass.LOOP_BEGIN:
                logging.debug('Parser: => token ' + token_num + ': LOOP BEGIN at ' + token.filename + '(' + str(token.line) + ')')
                if token.inlined == True:
                    logging.debug('Parser: skipping inlined loop')
                    self.skip_loop()
                else:
                    # get inner Loop object to fill with the information parsed out of incoming loop report
                    loop_name = Loop.form_main_loop_name(token.filename, token.line)

                    if loop.filename == token.filename and loop.line == token.line:
                        loop.classification.tiling_count += 1 
                        # loop tiling optimization
                        continue

                    inner_loop = self.loop_nest_struct.get_loop(loop_name)
                    if inner_loop == None:
                        # haven't seen any parts of this loop yet
                        # inherit the type from a parent loop
                        loop_type = loop.loop_type
                        num = 0 
                        loop_depth = loop.depth + 1
                        
                        inner_loop = Loop(token.filename, token.line, loop_depth, loop_type, num)
                        
                        if loop.add_inner_loop(inner_loop) == False:
                            sys.exit("error: ir: could not add Loop obj " + str(inner_loop) + " " + token.filename + "(" + str(token.line) + ")" + " to Loop.inner_loops")
                        if loop_type == LoopType.MAIN:
                            if self.loop_nest_struct.add_loop(inner_loop) == False:
                                sys.exit("error: ir: could not add Loop obj " + str(inner_loop) + " " + token.filename + "(" + str(token.line) + ")" + " to LoopNestingStructure IR.loops")
                        inner_loop.set_loop_nest_struct(self.loop_nest_struct)
                    elif loop.get_inner_loop(loop_name) == None:
                        if loop.add_inner_loop(inner_loop) == False:
                            sys.exit("error: ir: could not add Loop obj " + str(inner_loop) + " " + token.filename + "(" + str(token.line) + ")" + " to Loop.inner_loops")

                    # parse loop
                    self.parse_loop_report(inner_loop)
                continue
            elif token.token_class == TokenClass.LOOP_END:
                logging.debug('Parser: => token ' + token_num + ': LOOP END')

                if loop.classification.tiling_count != 0:
                    loop.classification.tiling = loop.classification.tiling_count

                while loop.classification.tiling_count > 0:
                    token = self.lexer.get_next_token()
                    token_num = '[' + str(self.lexer.get_token_num()) + ']'
                    if token.token_class == TokenClass.LOOP_END:
                        logging.debug('Parser: => token ' + token_num + ': LOOP END')
                    else:
                        sys.exit("error: parser: loop tiling LOOP END processing")
                    loop.classification.tiling_count -= 1
                # loop is done with
                break
            elif token.token_class == TokenClass.LOOP_PART_TAG:
                logging.debug('Parser: => token ' + token_num + ': loop partition tag')
                old_loop = loop
                loop = self.parse_loop_partition_tag(loop, token)
                if loop is old_loop:
                    if token.tag_type != LoopPartTagType.DISTR_CHUNK or token.chunk_num != 1:
                        sys.exit("error: parser: loop partition tag is supposed to create a new loop in a loop nesting structure")
                continue
            else:
                sys.exit("error: parser: unrecognised token has been encountered")
        
        return
            
    def parse_loop_partition_tag(self, loop, token):

        # swap an object loop pointer points to;
        # main loop component -> loop part;
        # all further ICC remarks in the current loop report scope
        # relate to a loop part object, rather than the main object;

        if token.token_class != TokenClass.LOOP_PART_TAG:
            sys.exit("error: parser: unrecognised token has been encountered")

        logging.debug('Parser: ===> parse_loop_partition_tag(loop=' + str(loop) + ')')
        logging.debug('Parser: loop at ' + loop.filename + '(' + str(loop.line) + ')')

        # <DistributedChunk([0-9]+)>
        if token.tag_type == LoopPartTagType.DISTR_CHUNK:
            num = token.chunk_num
            distr_chunk_loop = loop.get_distr_chunk(num)
            if distr_chunk_loop == None:
                if num == 1:
                    # distributed chunk 1 is treated as the main loop
                    distr_chunk_loop = loop
                    loop.add_distr_chunk(distr_chunk_loop, num)
                else:
                    loop_type = LoopType.DISTR
                    distr_chunk_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
                    loop.add_distr_chunk(distr_chunk_loop, num)
            return distr_chunk_loop 

        # loop distributed chunk vector remainder
        if token.tag_type == LoopPartTagType.DISTR_CHUNK_VECTOR_REMAINDER:
            num = token.chunk_num
            distr_chunk_loop = loop.get_distr_chunk(num)
            if distr_chunk_loop == None:
                if num == 1:
                    # distributed chunk 1 is treated as the main loop
                    distr_chunk_loop = loop
                    loop.add_distr_chunk(distr_chunk_loop, num)
                else:
                    loop_type = LoopType.DISTR
                    distr_chunk_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
                    loop.add_distr_chunk(distr_chunk_loop, num)
            loop_type = LoopType.VECTOR_REMAINDER
            distr_chunk_remainder_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
            distr_chunk_loop.add_vector_remainder_loop(distr_chunk_remainder_loop)
            return distr_chunk_remainder_loop 
 
        # loop distributed chunk remainder
        if token.tag_type == LoopPartTagType.DISTR_CHUNK_REMAINDER:
            num = token.chunk_num
            distr_chunk_loop = loop.get_distr_chunk(num)
            if distr_chunk_loop == None:
                if num == 1:
                    # distributed chunk 1 is treated as the main loop
                    distr_chunk_loop = loop
                    loop.add_distr_chunk(distr_chunk_loop, num)
                else:
                    loop_type = LoopType.DISTR
                    distr_chunk_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
                    loop.add_distr_chunk(distr_chunk_loop, num)
            loop_type = LoopType.REMAINDER
            distr_chunk_remainder_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
            distr_chunk_loop.add_remainder_loop(distr_chunk_remainder_loop)
            return distr_chunk_remainder_loop 
       
        # loop peel
        if token.tag_type == LoopPartTagType.PEEL:
            peel_loop = loop.get_peel_loop()
            if peel_loop == None:
                loop_type = LoopType.PEEL
                num = 0
                peel_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, num)
                loop.add_peel_loop(peel_loop)
            return peel_loop

        # loop vectorization remainder
        if token.tag_type == LoopPartTagType.VECTOR_REMAINDER:
            remainder_loop = loop.get_vector_remainder_loop()
            if remainder_loop == None:
                loop_type = LoopType.VECTOR_REMAINDER
                remainder_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, 0)
                loop.add_remainder_loop(remainder_loop)
            return remainder_loop
      
        # loop remainder
        if token.tag_type == LoopPartTagType.REMAINDER:
            remainder_loop = loop.get_remainder_loop()
            if remainder_loop == None:
                loop_type = LoopType.REMAINDER
                remainder_loop = Loop(loop.filename, loop.line, loop.depth, loop_type, 0)
                loop.add_remainder_loop(remainder_loop)
            return remainder_loop

        return

    def parse_loop_remark(self, loop, token):

        if token.token_class != TokenClass.LOOP_REMARK:
            sys.exit("error: parser: token must be of LOOP REMARK type")

        logging.debug('Parser: ' + token.remark_type.name)
        
        # parallel  
        if token.remark_type == LoopRemarkType.PARALLEL:
            loop.classification.set_parallel(Classification.YES)
        elif token.remark_type == LoopRemarkType.PARALLEL_POTENTIAL:
            loop.classification.set_parallel_potential(Classification.YES)
        # vector
        elif token.remark_type == LoopRemarkType.VECTOR:
            loop.classification.set_vector(Classification.YES)
        elif token.remark_type == LoopRemarkType.VECTOR_POTENTIAL:
            loop.classification.set_vector_potential(Classification.YES)
        # dependence
        elif token.remark_type == LoopRemarkType.PARALLEL_DEPENDENCE:
            loop.classification.set_parallel_dependence(Classification.YES)
        elif token.remark_type == LoopRemarkType.VECTOR_DEPENDENCE:
            loop.classification.set_vector_dependence(Classification.YES)
        # loop fusion
        elif token.remark_type == LoopRemarkType.LOOP_FUSION_MAIN:
            loop.classification.fused = Classification.YES
            loop.classification.fused_with = token.fused_list
        elif token.remark_type == LoopRemarkType.LOOP_FUSION_LOST:
            loop.classification.fused_lost = Classification.YES
        # loop distribution
        elif token.remark_type == LoopRemarkType.LOOP_DISTRIBUTION_MARK:
            loop.classification.distr = Classification.YES
            loop.classification.distr_parts_n = token.distr_num

        return

if __name__ == "__main__":
    pass
else:
    pass
