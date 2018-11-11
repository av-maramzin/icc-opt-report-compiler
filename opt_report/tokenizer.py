#! /usr/bin/python3

from regex import *

class TokenClass(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report token class """
    
    UNDEFINED = 0
    LOOP_BEGIN = 1
    LOOP_END = 2
    LOOP_PART_TAG = 3
    LOOP_REMARK = 4
    EOR = 5 # end of report 

class PartitionTagType(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report partition tag type """
    
    DISTR_CHUNK = 0
    DISTR_CHUNK_VECTOR_REMAINDER = 0
    PEEL = 1
    VECTOR_REMAINDER = 2
    REMAINDER = 3

class LoopRemarkType(Enum):
    
    """ Intel C/C++ Compiler (ICC) optimization report remark type """
    
    SKIP = 0
    PARALLEL = 1
    PARALLEL_POTENTIAL = 2
    VECTOR = 3
    VECTOR_POTENTIAL = 4
    PARALLEL_DEPENDENCE = 5
    VECTOR_DEPENDENCE = 6

class Token:

    """ Intel C/C++ Compiler (ICC) optimization report token """

    def __init__(self, token_class=TokenClass.UNDEFINED, lexeme=""):
        self.token_class = token_class
        self.lexeme = lexeme
        
    def get_token_class():
        return self.token_class

    def get_lexeme():
        return self.lexeme

class Tokeniser:

    """ Intel C/C++ Compiler (ICC) optimization report tokeniser """

    def __init__(self, lexer):
        self.lexer = lexer # lexer reference

    def tokenise_lexeme(lexeme):
 
        re_match = None
        token = None

        # [1] Check if a current lexeme signifies beginning of a loop report

        # loop begin
        re_match = LOOP_BEGIN_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_BEGIN, lexeme)
            token.filename = re_match.group(1)
            token.line = re_match.group(2)
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
            token.tag_type = PartitionTagType.DISTR_CHUNK
            token.chunk_num = re_match.group(1)
            return token
        
        # loop distributed chunk remainder
        re_match = LOOP_DISTR_CHUNK_VECTOR_REMAINDER_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = PartitionTagType.DISTR_CHUNK_VECTOR_REMAINDER
            token.chunk_num = re_match.group(1)
            return token

        # loop peel
        re_match = LOOP_PEEL_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = PartitionTagType.PEEL
            return token
 
        # loop vectorization remainder
        re_match = LOOP_VECTOR_REMAINDER_re.search(line)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = PartitionTagType.VECTOR_REMAINDER
            return token
       
        # loop remainder
        re_match = LOOP_REMAINDER_re.search(line)
        if re_match != None:
            token = Token(TokenClass.LOOP_PART_TAG, lexeme)
            token.tag_type = PartitionTagType.REMAINDER
            return token
           
        # [3] Check if the current lexeme is a loop remark
            
        # loop parallel
        re_match = LOOP_PARALLEL_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.PARALLEL
            return token

        # loop parallel potential
        re_match = LOOP_PARALLEL_POTENTIAL_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.PARALLEL_POTENTIAL
            return token

        # loop vector
        re_match = LOOP_VECTOR_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.VECTOR
            return token

        # loop vector potential
        re_match = LOOP_VECTOR_POTENTIAL_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.VECTOR_POTENTIAL
            return token

        # loop paralel dependence
        re_match = LOOP_PARALLEL_DEPENCENCE_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.PARALLEL_DEPENDENCE
            return token

        # loop vector dependence
        re_match = LOOP_VECTOR_DEPENCENCE_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_REMARK, lexeme)
            token.remark_type = LoopRemarkType.VECTOR_DEPENDENCE
            return token

        # [4] Check if the current lexeme signifies the end of a loop report

        # loop end
        re_match = LOOP_END_re.search(lexeme)
        if re_match != None:
            token = Token(TokenClass.LOOP_END, lexeme)
            return token
        
        # current lexeme has not triggered a match against any of 
        # the types we are interested in -> return token to skip
        token = Token(TokenClass.SKIP, lexeme)
        return token

