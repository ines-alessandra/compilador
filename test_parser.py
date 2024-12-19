# test_parser.py

import unittest
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from ast import Program

class TestParser(unittest.TestCase):
    def test_simple_var_decl(self):
        code = "val x : Int = 10;"
        lexer = Lexer(code)
        lexer.tokenize()
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.declarations), 1)
        self.assertEqual(ast.declarations[0].name, "x")

    def test_missing_semicolon(self):
        code = "val x : Int = 10"
        lexer = Lexer(code)
        lexer.tokenize()
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertTrue(len(parser.errors) > 0)
        self.assertIn("Esperado ';' após a declaração da variável.", str(parser.errors[0]))

if __name__ == '__main__':
    unittest.main()
