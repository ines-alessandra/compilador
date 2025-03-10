from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator

def main():
    try:
        # Lê o código do arquivo
        with open('./teste.kt', 'r') as file:
            code = file.read()

        # Executa o lexer
        lexer = Lexer(code)
        lexer.tokenize()
        tokens = lexer.list_tokens
        
        print("Tokens gerados pelo lexer:")
        for token in tokens:
            print(token)

        # Inicializa o parser com os tokens
        parser = Parser(tokens)
        ast = parser.parse()

        # Executa a análise semântica
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)

        # Se a análise semântica passou, gera o código
        generator = CodeGenerator()
        generator.generate(ast)
        
    except LexerError as le:
        print(f"Erro léxico: {le}")
    except ParserError as pe:
        print(f"Erro de análise sintática: {pe}")
    except SemanticError as se:
        print(f"Erro semântico: {se}")

if __name__ == '__main__':
    main()
