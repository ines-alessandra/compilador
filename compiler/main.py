from lexer import Lexer
from parser import Parser
from code_generator import ThreeAddressCodeGenerator
import json
# from ast_utils import save_ast_to_file, print_ast


def main():
    try:
        # Lê o código do arquivo
        with open('./teste.kt', 'r') as file:
            code = file.read()

        # Executa o lexer
        lexer = Lexer(code)
        lexer.tokenize()
        # tokens = lexer.list_tokens

        # Inicializa o parser com os tokens
        # parser = Parser(tokens)
        parser = Parser()
        parser.parse(lexer.tokens_list)
        tac_generator = ThreeAddressCodeGenerator()
        tac_generator.start(parser.instructions)
        # ast = parser.parse()

        # # Executa a análise semântica
        # semantic_analyzer = SemanticAnalyzer()
        # semantic_analyzer.analyze(ast)
    

        # save_ast_to_file(ast, 'ast_output.json')

        
        # print("A saída semântica foi salva em 'saida_semantica.json'.")
        # Se a análise semântica passou, gera o código
        # generator = ThreeAddressCodeGenerator()
        # generator.generate(ast)
    except FileNotFoundError:
        print("Arquivo não encontrado. Verifique o caminho do arquivo.")
    except SyntaxError as se:
        print(f"Erro de sintaxe: {se}")
    # except LexerError as le:
    #     print(f"Erro léxico: {le}")
    # except ParserError as pe:
    #     print(f"Erro de análise sintática: {pe}")
    # except SemanticError as se:
    #     print(f"Erro semântico: {se}")

if __name__ == '__main__':
    main()
