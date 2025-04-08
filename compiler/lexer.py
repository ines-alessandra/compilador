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
    def __init__(self, token_type, value, line):
        self.token_type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', {self.line})"


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens_list: list[Token] = []
        #self.symbol_table: dict[Token, dict[str, Any]] = {}
        self.patterns: List[Tuple[str, str]] = tokens

    def tokenize(self):
        #Itera linha a linha
        for current_line, line in enumerate(self.code.splitlines()):
            line_tokens = self.__line_to_tokens(line, current_line + 1)
            self.tokens_list.extend(line_tokens)

    def __line_to_tokens(self, line: str, line_number: int) -> List[Token]:
        line = line.strip()
        line_tokens = []

        #Percorre a linha
        while line:
            matched = False

            #Verifica se pelo menos uma das expressões regulares é aceita
            for pattern, token_type in self.patterns:
                match = re.match(pattern, line)
                if match:
                    matched = True
                    value = match.group(0)
                    token = Token(token_type=token_type, value=value, line=line_number)

                    #self.__handle_token(token, line_number)

                    line_tokens.append(token)
                    # Corta a parte do token que foi aceita e espaços vazios
                    line = line[len(value):].strip()
                    break

            if not matched:
                raise ValueError(f"Invalid syntax at line {line_number} >>>>> {line}")

        return line_tokens

    #def __handle_token(self, token: Token, line_number: int):
    #    if token.token_type == "IDENTIFIER":
    #        self.symbol_table[token] = {
    #            "identifier_type": None,
    #            "variable_type": None,
    #            "variable_value": None,
    #            "scope": None,
    #            "line": line_number,
    #        }
