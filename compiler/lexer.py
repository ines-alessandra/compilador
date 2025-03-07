import re
from typing import List, Tuple
from Token import Token

tokens = [
    # reserved tokens
    (r"\bif\b", "IF"),
    (r"\belse\b", "ELSE"),

    (r"\bwhile\b", "WHILE"),
    (r"\bbreak\b", "BREAK"),
    (r"\bcontinue\b", "CONTINUE"),

    (r"\bconst\b", "CONST"),
    (r"\bval\b", "VARIABLE"),

    (r"\bInt\b", "INT"),
    (r"\bBool\b", "BOOL"),

    (r"\btrue\b", "TRUE"),
    (r"\bfalse\b", "FALSE"),

    (r"\bfun\b", "FUNCTION"),
    (r"\breturn\b", "RETURN"),

    (r"\bprint\b", "PRINT"),

    # symbols
    (r":", "COLON"),
    (r"==", "EQUAL"),
    (r"!=", "DIFFERENT"),
    (r">=", "GREATER_OR_EQUAL"),
    (r"<=", "LESS_OR_EQUAL"),
    (r"\+", "PLUS"),
    (r"-", "MINUS"),
    (r"\*", "MULTIPLY"),
    (r"/", "DIVIDE"),
    (r"=", "ASSIGN"),
    (r",", "COMMA"),
    (r";", "SEMICOLON"),
    (r"\(", "LPAREN"),
    (r"\)", "RPAREN"),
    (r">", "GREATER"),
    (r"<", "LESS"),
    (r"\{", "LBRACE"),
    (r"\}", "RBRACE"),
    # others
    (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "IDENTIFIER"),
    (r"\b[0-9]+\b", "INTEGER"),
]

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} (linha {line}, coluna {column})")


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.list_tokens: list[Token] = []
        self.rules: List[Tuple[str, str]] = tokens
    
    def tokenize(self):
        lines = self.code.split("\n")
        for i, line in enumerate(lines):
            
            self.tokenize_line(line, i +1)
            
    
    def tokenize_line(self, line: str, line_number: int):
        line_tokens = []
        line = line.strip()
        position = 0

        while line:
            find = False
            for rule, type in self.rules:
                match = re.match(rule, line)
                if match:
                    find = True
                    value = match.group(0)
                    line_tokens.append(Token(type, value, line_number))
                    position += len(value)
                    line = line[len(value):].strip()
                    break

            if not find:
                column = position + 1
                raise LexerError(f"Erro, token inesperado: '{line[0]}'", line_number + 1, column)

        self.list_tokens.extend(line_tokens)

    def print_tokens(self):
        for token in self.list_tokens:
            print(token)

                
if __name__ == "__main__":
    # Código de exemplo para teste
    code = """
    ,  + - * / = == != > < >= <= ( ) { } : , ; .
    """
    try:
        lexer = Lexer(code)
        lexer.tokenize()
        lexer.print_tokens()
    except LexerError as e:
        print(e)
