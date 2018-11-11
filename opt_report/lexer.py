#! /usr/bin/python3

from scanner import Scanner
from tokeniser import Tokeniser

class Lexer:

    """ Intel C/C++ Compiler optimization report lexical analyser  """

    def __init__(self, report_filename = ""):
        self.scanner = Scanner(self, report_filename)
        self.tokeniser = Tokeniser(self)

    def get_next_token():
        return self.tokeniser.tokenise_lexeme( self.scanner.get_next_lexeme() )

if __name__ == "__main__":
    print("Lexer class defined!")
else:
    pass
