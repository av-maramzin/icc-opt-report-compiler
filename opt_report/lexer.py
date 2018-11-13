#! /usr/bin/python3

import sys

from scanner import Scanner
from tokeniser import Tokeniser, Token, TokenClass

class Lexer:

    """ Intel C/C++ Compiler optimization report lexical analyser  """

    def __init__(self, report_filename = ""):
        self.report_filename = report_filename
        self.scanner = Scanner(self, self.report_filename)
        self.tokeniser = Tokeniser(self)
        self.token_num = 0

    def get_next_token(self):
        token = self.tokeniser.tokenise_lexeme( self.scanner.get_next_lexeme() )
        if token != TokenClass.EOR:
            self.token_num += 1
        return token

if __name__ == "__main__":
    
    print("= Intel C/C++ Compiler optimization report Lexer =")
    print("Produces a list of tokens found in the provided optimization report file")

    print("=> intel_compiler.opt_report.lexer DEBUG mode")

    if len(sys.argv) != 2:
        error_str = "error: "
        error_str += "lexer: "
        error_str += "incorrect argument list => use ./lexer opt-report-filename"
        sys.exit(error_str)

    lexer = Lexer(sys.argv[1])

    while True:
        
        token = lexer.get_next_token()

        if token.token_class != TokenClass.EOR:
            lexer.tokeniser.print_token(token)
            continue
        else:
            lexer.tokeniser.print_token(token)
            break
    
    print("=> intel_compiler.opt_report.lexer DEBUG mode finished!")
    sys.exit()

else:
    pass
