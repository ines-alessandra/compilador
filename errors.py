# errors.py

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"LexerError at line {line}, column {column}: {message}")
        self.line = line
        self.column = column

class ParserError(Exception):
    def __init__(self, message: str, token):
        if token:
            super().__init__(f"[Linha {token.line}, Coluna {token.column}] Erro: {message} (Token atual: '{token.value}')")
        else:
            super().__init__(f"Erro: {message}")
