#! /usr/bin/python3

import sys
from enum import Enum

from scanner import Scanner

from regex import *

from ir import LoopType

class TokenClass(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report token class """
    
    UNDEFINED = 0
    SKIP = 1
    LOOP_BEGIN = 2
    LOOP_END = 3
    LOOP_PART_TAG = 4
    LOOP_REMARK = 5
    EOR = 6 # end of report 

class LoopPartTagType(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report loop partition tag type """
    
    DISTR_CHUNK = 0
    DISTR_CHUNK_VECTOR_REMAINDER = 1
    PEEL = 2
    VECTOR_REMAINDER = 3
    REMAINDER = 4

class LoopRemarkType(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report loop remark type """
    
    SKIP = 0
    PARALLEL = 1
    PARALLEL_POTENTIAL = 2
    VECTOR = 3
    VECTOR_POTENTIAL = 4
    PARALLEL_DEPENDENCE = 5
    VECTOR_DEPENDENCE = 6
    LOOP_FUSION_MAIN = 7
    LOOP_FUSION_LOST = 8
    LOOP_DISTRIBUTION_MARK = 9

class Token:

    """ Intel C/C++ Compiler (ICC) optimization report token """

    def __init__(self, token_class=TokenClass.UNDEFINED, lexeme=""):
        self.token_class = token_class
        self.lexeme = lexeme
        
    def get_token_class(self):
        return self.token_class

    def get_lexeme(self):
        return self.lexeme

class Tokeniser:

    """ Intel C/C++ Compiler (ICC) optimization report Tokeniser """

    def __init__(self, lexer=None):
        self.lexer = lexer # lexer reference

    def print_token(self, token):

        print("token {")
        print("\t" + str(token.token_class))
        if token.token_class == TokenClass.SKIP:
            pass
        elif token.token_class == TokenClass.LOOP_REMARK:
            print("\t" + "loop remark #" + str(token.remark_num) + ": " + str(token.remark))
            print("\t" + "remark type: " + str(token.remark_type))
            if token.remark_type == LoopRemarkType.PARALLEL or token.remark_type == LoopRemarkType.VECTOR:
                print("\t" + "loop type: " + str(token.loop_type))
            elif token.remark_type == LoopRemarkType.LOOP_FUSION_MAIN:
                fused_list_str = "[ "
                for s in token.fused_list:
                    fused_list_str += str(s)
                    fused_list_str += " "
                fused_list_str += "]"
                print("\t" + "fused loops: " + fused_list_str)
            elif token.remark_type == LoopRemarkType.LOOP_DISTRIBUTION_MARK:
                print("\t" + "distributed ways: " + str(token.distr_num))

        elif token.token_class == TokenClass.LOOP_BEGIN:
            print("\t" + "loop filename: " + str(token.filename))
            print("\t" + "loop line: " + str(token.line))
            print("\t" + "inlined: " + str(token.inlined))
            if token.inlined == True:
                print("\t" + "inlined into filename: " + str(token.inlined_filename))
                print("\t" + "inlined into line: " + str(token.inlined_line))
        elif token.token_class == TokenClass.LOOP_END:
            pass
        elif token.token_class == TokenClass.LOOP_PART_TAG:
            print("\t" + "tag type: " + str(token.tag_type))
            if token.tag_type == LoopPartTagType.DISTR_CHUNK or token.tag_type == LoopPartTagType.DISTR_CHUNK_VECTOR_REMAINDER:
                print("\t" + "distr chunk number: " + str(token.chunk_num))
        elif token.token_class == TokenClass.EOR:
            print("\t" + "END OF REPORT")
        elif token.token_class == TokenClass.UNDEFINED:
            print("\t" + "undefined")
        
        print("}")

    def tokenise_lexeme(self, lexeme):
 
        re_match = None
        token = None

        # [ script performance optimization ]
        # the order of matching checks in the code below approximately
        # corresponds to the frequency of their encounter in the ICC report 
        
        # [3] Check if the current lexeme is a loop remark
        re_match = LOOP_REMARK_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_num = re_match.group(1)
            token.remark = re_match.group(2)
            
            # loop was auto-parallelized
            re_match = LOOP_PARALLEL_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.PARALLEL

                re_match = LOOP_DISTR_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.DISTR
                    return token

                re_match = LOOP_FUSED_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.FUSED
                    return token

                re_match = LOOP_PARTIAL_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.PARTIAL
                    return token

                token.loop_type = LoopType.MAIN
                return token

            # loop was vectorized
            re_match = LOOP_VECTOR_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.VECTOR

                re_match = LOOP_DISTR_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.DISTR
                    return token

                re_match = LOOP_FUSED_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.FUSED
                    return token

                re_match = LOOP_PARTIAL_re.search(token.remark)
                if re_match != None:
                    token.loop_type = LoopType.PARTIAL
                    return token

                token.loop_type = LoopType.MAIN
                return token

            # loop was not parallelized: inner loop
            re_match = LOOP_PARALLEL_POTENTIAL_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.PARALLEL_POTENTIAL
                return token

            # loop was not vectorized: inner loop was already vectorized 
            re_match = LOOP_VECTOR_POTENTIAL_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.VECTOR_POTENTIAL
                return token

            # loop parallel dependence
            re_match = LOOP_PARALLEL_DEPENCENCE_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.PARALLEL_DEPENDENCE
                return token

            # loop vector dependence
            re_match = LOOP_VECTOR_DEPENDENCE_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.VECTOR_DEPENDENCE
                return token

            # loop fusion optimization
            re_match = LOOP_FUSION_MAIN_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.LOOP_FUSION_MAIN
                fused_loops_str = re_match.group(1)
                token.fused_list =  [int(s) for s in fused_loops_str.split() if s.isdigit()]
                return token

            re_match = LOOP_FUSION_LOST_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.LOOP_FUSION_LOST
                return token

            # loop distribution optimization
            re_match = LOOP_DISTRIBUTION_MARK_re.search(token.remark)
            if re_match != None:
                token.remark_type = LoopRemarkType.LOOP_DISTRIBUTION_MARK
                token.distr_num = re_match.group(1)
                return token

            # remark we are not currently interested in
            token.remark_type = LoopRemarkType.SKIP
            return token

        # [1] Check if the current lexeme signifies beginning of a loop report

        # loop begin
        re_match = LOOP_BEGIN_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_BEGIN, lexeme)
            token.filename = re_match.group(1)
            token.line = re_match.group(2)
            token.inlined = False
            return token

        # loop begin inlined into
        re_match = LOOP_BEGIN_INLINED_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_BEGIN, lexeme)
            token.filename = re_match.group(1)
            token.line = re_match.group(2)
            token.inlined = True
            token.inlined_filename = re_match.group(4)
            token.inlined_line = re_match.group(5)
            return token

        # [2] Check if a current lexeme tags a loop as a loop partition
        
        # <DistributedChunk([0-9]+)>
        re_match = LOOP_DISTR_CHUNK_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = LoopPartTagType.DISTR_CHUNK
            token.chunk_num = re_match.group(1)
            return token
        
        # loop distributed chunk remainder
        re_match = LOOP_DISTR_CHUNK_VECTOR_REMAINDER_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = LoopPartTagType.DISTR_CHUNK_VECTOR_REMAINDER
            token.chunk_num = re_match.group(1)
            return token

        # loop peel
        re_match = LOOP_PEEL_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = LoopPartTagType.PEEL
            return token
 
        # loop vectorization remainder
        re_match = LOOP_VECTOR_REMAINDER_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = LoopPartTagType.VECTOR_REMAINDER
            return token
       
        # loop remainder
        re_match = LOOP_REMAINDER_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = LoopPartTagType.REMAINDER
            return token

        # [4] Check if the current lexeme signifies the end of a loop report or the whole report

        # loop report end
        re_match = LOOP_END_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_END, lexeme)
            return token
        
        # report end
        if lexeme == "":
            token = Token(TokenClass.EOR, lexeme)
            return token

        # current lexeme has not triggered a match against any of 
        # the types we are interested in -> return token to skip
        token = Token(TokenClass.SKIP, lexeme)
        return token

if __name__ == "__main__":
    
    print("= Intel C/C++ Compiler optimization report Tokeniser =")
    print("Produces a list of tokens found in the provided optimization report file\n")

    print("=> intel_compiler.opt_report.tokeniser DEBUG mode\n")

    if len(sys.argv) != 2:
        error_str = "error: "
        error_str += "tokeniser: "
        error_str += "incorrect argument list => use ./tokeniser opt-report-filename"
        sys.exit(error_str)

    scanner = Scanner(None, sys.argv[1])
    tokeniser = Tokeniser()

    while True:
       
        token = tokeniser.tokenise_lexeme( scanner.get_next_lexeme() )

        if token.token_class != TokenClass.EOR:
            tokeniser.print_token(token)
            print("")
            continue
        else:
            tokeniser.print_token(token)
            print("")
            break
    
    print("=> intel_compiler.opt_report.tokeniser DEBUG mode finished!")
    sys.exit()

else:
    pass
