import re
from typing import List, Tuple

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

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', line={self.line})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.list_tokens: list[Token] = []
        self.rules: List[Tuple[str, str]] = tokens
    
    def tokenize(self):
        lines = self.code.split("\n")
        for i, line in enumerate(lines):
            self.tokenize_line(line, i)
    
    def tokenize_line(self, line: str, line_number: int):
        line_tokens = []
        line = line.strip()

        while line:
            find = False
            for rule, type in self.rules:
                match = re.match(rule, line)
                if match:
                    find = True
                    value = match.group(0)
                    line_tokens.append(Token(type, value, line_number))
                    line = line[len(value):]
                    line = line.strip()
                    break

            if not find:
                print(f"Error: Unexpected token at line {line_number} : {line}")
                break
        
        self.list_tokens.extend(line_tokens)


