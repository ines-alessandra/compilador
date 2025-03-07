from lexer import Lexer, LexerError
from parser import (
    Parser, ParserError, Program, VarDecl, FuncDecl, Block,
    Assignment, IfStatement, WhileStatement, ReturnStatement,
    BreakStatement, ContinueStatement, PrintStatement,
    BinaryOp, UnaryOp, Literal, Identifier, FuncCall
)

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

        print("\nAST Gerada pelo parser:")
        print_ast(ast)
        generator = CodeGenerator()
        generator.generate(ast)  # ast_root é o Program gerado pelo seu parser

        
        
    except LexerError as le:
        print(f"Erro léxico: {le}")
        return  # Para a execução imediatamente após o erro
    except ParserError as pe:
        print(f"Erro de análise sintática: {pe}")
        return  # Para a execução imediatamente após o erro

def print_ast(node, indent=0):
    prefix = ' ' * indent
    if isinstance(node, Program):
        print(f"{prefix}Program")
        for decl in node.declarations:
            print_ast(decl, indent + 2)
    elif isinstance(node, VarDecl):
        const_str = "const" if node.is_const else "val"
        print(f"{prefix}{const_str} {node.name} : {node.var_type} =")
        print_ast(node.initializer, indent + 2)
    elif isinstance(node, FuncDecl):
        params = ', '.join([f"{name}: {type_}" for name, type_ in node.params])
        print(f"{prefix}fun {node.name}({params}) : {node.return_type} {{")
        print_ast(node.body, indent + 2)
        print(f"{prefix}}}")
    elif isinstance(node, Block):
        for decl in node.declarations:
            print_ast(decl, indent)
    elif isinstance(node, Assignment):
        print(f"{prefix}{node.name} =")
        print_ast(node.value, indent + 2)
    elif isinstance(node, IfStatement):
        print(f"{prefix}if (")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}) {{")
        print_ast(node.then_branch, indent + 2)
        print(f"{prefix}}}")
        if node.else_branch:
            print(f"{prefix}else {{")
            print_ast(node.else_branch, indent + 2)
            print(f"{prefix}}}")
    elif isinstance(node, WhileStatement):
        print(f"{prefix}while (")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}) {{")
        print_ast(node.body, indent + 2)
        print(f"{prefix}}}")
    elif isinstance(node, ReturnStatement):
        print(f"{prefix}return")
        print_ast(node.value, indent + 2)
    elif isinstance(node, BreakStatement):
        print(f"{prefix}break")
    elif isinstance(node, ContinueStatement):
        print(f"{prefix}continue")
    elif isinstance(node, PrintStatement):
        print(f"{prefix}print(")
        print_ast(node.value, indent + 2)
        print(f"{prefix});")
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp: {node.operator}")
        print_ast(node.left, indent + 2)
        print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp: {node.operator}")
        print_ast(node.operand, indent + 2)
    elif isinstance(node, Literal):
        print(f"{prefix}Literal: {node.value}")
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier: {node.name}")
    elif isinstance(node, FuncCall):
        print(f"{prefix}FuncCall: {node.name}(")
        for arg in node.args:
            print_ast(arg, indent + 2)
        print(f"{prefix})")
    else:
        print(f"{prefix}Unknown node: {node}")

if __name__ == '__main__':
    main()
