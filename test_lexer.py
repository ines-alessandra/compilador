# test_lexer.py

import unittest
from lexer import Lexer, LexerError

class TestLexer(unittest.TestCase):
    def test_valid_tokens(self):
        code = "val x : Int = 10;"
        lexer = Lexer(code)
        lexer.tokenize()
        tokens = lexer.get_tokens()
        expected_types = ["VARIABLE", "IDENTIFIER", "COLON", "INT", "ASSIGN", "INTEGER", "SEMICOLON"]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_invalid_token(self):
        code = "val x @ : Int = 10;"
        lexer = Lexer(code)
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
        self.assertIn("Unexpected token '@'", str(context.exception))

if __name__ == '__main__':
    unittest.main()
