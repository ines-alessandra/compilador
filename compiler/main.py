from lexer import Lexer
from parser import Parser, SemanticError
from tac_generator import ThreeAddressCodeGenerator

def main():
    try:
        # Lê o código do arquivo
        with open('./teste3.kt', 'r') as file:
            code = file.read()

        # Executa o lexer
        lexer = Lexer(code)
        lexer.tokenize()

        parser = Parser()
        parser.parse(lexer.tokens_list)
        tac_generator = ThreeAddressCodeGenerator()
        tac_generator.start(parser.instructions)      

    except FileNotFoundError:
        print("Arquivo não encontrado. Verifique o caminho do arquivo.")
    except SyntaxError as se:
        print(f"Erro de sintaxe: {se}")
    except SemanticError as seme:
        print(f"Erro semântico: {seme}")  # ⬅ isso aqui limpa a saída!

if __name__ == '__main__':
    main()
