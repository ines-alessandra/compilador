# parser.py

from typing import List, Optional
from lexer import Token

class ParserError(Exception):
    def __init__(self, message, token: Optional[Token] = None):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

    def __str__(self):
        if self.token:
            return f"[Linha {self.token.line}] Erro: {self.message} (Token atual: {self.token})"
        return f"Erro: {self.message}"

# Definição dos nós da AST
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode]):
        self.declarations = declarations

class VarDecl(ASTNode):
    def __init__(self, is_const: bool, name: str, var_type: str, initializer: ASTNode):
        self.is_const = is_const
        self.name = name
        self.var_type = var_type
        self.initializer = initializer

class FuncDecl(ASTNode):
    def __init__(self, name: str, params: List[tuple], return_type: str = "Unit", body: ASTNode = None):
        self.name = name
        self.params = params  # Lista de tuplas (nome, tipo)
        self.return_type = return_type
        self.body = body

class Block(ASTNode):
    def __init__(self, declarations: List[ASTNode]):
        self.declarations = declarations

class Assignment(ASTNode):
    def __init__(self, name: str, value: ASTNode):
        self.name = name
        self.value = value

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: Optional[ASTNode]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode):
        self.condition = condition
        self.body = body

class ReturnStatement(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

class BreakStatement(ASTNode):
    pass

class ContinueStatement(ASTNode):
    pass

class PrintStatement(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

class Expression(ASTNode):
    pass

class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

class Literal(Expression):
    def __init__(self, value):
        self.value = value

class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

class FuncCall(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.scope_stack = [{}]

    def parse(self) -> Program:
        declarations = []
        while not self.is_at_end():
            decl = self.declaration()
            declarations.append(decl)
        return Program(declarations)

    def enter_scope(self):
        self.scope_stack.append({})
    def exit_scope(self):
        self.scope_stack.pop()
    def add_to_scope(self, name, var_type=None, is_const=False, is_function=False, params=None, return_type=None):
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            raise ParserError(f"Identificador '{name}' já declarado no escopo atual.", self.peek())
        current_scope[name] = {
            "type": var_type,
            "is_const": is_const,
            "is_function": is_function,
            "params": params,
            "return_type": return_type,
        }

    def lookup_in_scope(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise ParserError(f"Identificador '{name}' não declarado.", self.peek())




    def declaration(self) -> ASTNode:
        if self.match("VARIABLE"):  # 'val'
            return self.var_decl(is_const=False)
        if self.match("CONST"):  # 'const'
            return self.var_decl(is_const=True)
        if self.match("FUNCTION"):  # 'fun'
            return self.func_decl()
        return self.statement()

    def var_decl(self, is_const: bool) -> VarDecl:
        name = self.consume("IDENTIFIER", "Esperado nome da variável.")
        self.consume("COLON", "Esperado ':' após o nome da variável.")
        var_type = self.consume_type()
        self.consume("ASSIGN", "Esperado '=' na declaração da variável.")
        initializer = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após a declaração da variável.")
        
        self.add_to_scope(name.value, var_type, is_const)
        
        return VarDecl(is_const, name.value, var_type, initializer)

    def func_decl(self) -> FuncDecl:
        name = self.consume("IDENTIFIER", "Esperado nome da função.")
        self.consume("LPAREN", "Esperado '(' após o nome da função.")
        
        params = []
        if not self.check("RPAREN"):
            params.append(self.parameter())
            while self.match("COMMA"):
                params.append(self.parameter())
        self.consume("RPAREN", "Esperado ')' após parâmetros da função.")
        
        # Tornar o tipo de retorno opcional
        if self.match("COLON"):
            return_type = self.consume_type()
        else:
            return_type = "Unit"  # Tipo de retorno padrão
        
        # Adicionar a função ao escopo atual
        self.add_to_scope(name.value, is_function=True, params=params, return_type=return_type)
        
        # Entrar no escopo do corpo da função
        self.enter_scope()
        # Adicionar os parâmetros ao escopo da função
        for param_name, param_type in params:
            self.add_to_scope(param_name, var_type=param_type)
        
        body = self.block()
        # Sair do escopo do corpo da função
        self.exit_scope()
        
        return FuncDecl(name.value, params, return_type, body)


    def parameter(self) -> tuple:
        name = self.consume("IDENTIFIER", "Esperado nome do parâmetro.")
        self.consume("COLON", "Esperado ':' após o nome do parâmetro.")
        param_type = self.consume_type()
        return (name.value, param_type)

    def block(self) -> Block:
        self.consume("LBRACE", "Esperado '{' para iniciar o bloco.")
        self.enter_scope() 
        declarations = []
        while not self.check("RBRACE") and not self.is_at_end():
            declarations.append(self.declaration())
        self.consume("RBRACE", "Esperado '}' para fechar o bloco.")
        self.exit_scope()
        return Block(declarations)

    def statement(self) -> ASTNode:
        if self.match("IF"):
            return self.if_statement()
        if self.match("WHILE"):
            return self.while_statement()
        if self.match("RETURN"):
            return self.return_statement()
        if self.match("BREAK"):
            self.consume("SEMICOLON", "Esperado ';' após 'break'.")
            return BreakStatement()
        if self.match("CONTINUE"):
            self.consume("SEMICOLON", "Esperado ';' após 'continue'.")
            return ContinueStatement()
        if self.match("PRINT"):
            return self.print_statement()
        
        # Verificar se a declaração é uma atribuição ou uma expressão
        if self.peek().type == "IDENTIFIER":
            if (self.current + 1) < len(self.tokens) and self.tokens[self.current + 1].type == "ASSIGN":
                return self.assignment()
            else:
                return self.expression_statement()
        
        # Caso não seja nenhuma das opções acima, erro
        raise ParserError("Esperado declaração ou instrução.", self.peek())

    def expression_statement(self) -> ASTNode:
        expr = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após expressão.")
        return expr

    def if_statement(self) -> IfStatement:
        self.consume("LPAREN", "Esperado '(' após 'if'.")
        condition = self.expression()
        self.consume("RPAREN", "Esperado ')' após condição do 'if'.")
        then_branch = self.block()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.block()
        return IfStatement(condition, then_branch, else_branch)

    def while_statement(self) -> WhileStatement:
        self.consume("LPAREN", "Esperado '(' após 'while'.")
        condition = self.expression()
        self.consume("RPAREN", "Esperado ')' após condição do 'while'.")
        body = self.block()
        return WhileStatement(condition, body)

    def return_statement(self) -> ReturnStatement:
        value = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após 'return'.")
        return ReturnStatement(value)

    def print_statement(self) -> PrintStatement:
        self.consume("LPAREN", "Esperado '(' após 'print'.")
        value = self.expression()
        self.consume("RPAREN", "Esperado ')' após expressão do 'print'.")
        self.consume("SEMICOLON", "Esperado ';' após 'print'.")
        return PrintStatement(value)

    def assignment(self) -> Assignment:
        name = self.consume("IDENTIFIER", "Esperado um identificador para atribuição.")
        # Verifica se o identificador existe no escopo atual ou global
        self.lookup_in_scope(name.value)  # Vai levantar um erro se não existir
        self.consume("ASSIGN", "Esperado '=' em atribuição.")
        value = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após atribuição.")
        return Assignment(name.value, value)


    def expression(self) -> Expression:
        return self.equality()

    def equality(self) -> Expression:
        expr = self.comparison()
        while self.match("EQUAL", "DIFFERENT"):
            operator = self.previous().type
            right = self.comparison()
            expr = BinaryOp(expr, operator, right)
        return expr

    def comparison(self) -> Expression:
        expr = self.term()
        while self.match("GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL"):
            operator = self.previous().type
            right = self.term()
            expr = BinaryOp(expr, operator, right)
        return expr

    def term(self) -> Expression:
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            operator = self.previous().type
            right = self.factor()
            expr = BinaryOp(expr, operator, right)
        return expr

    def factor(self) -> Expression:
        expr = self.unary()
        while self.match("MULTIPLY", "DIVIDE"):
            operator = self.previous().type
            right = self.unary()
            expr = BinaryOp(expr, operator, right)
        return expr

    def unary(self) -> Expression:
        if self.match("MINUS", "NOT"):
            operator = self.previous().type
            operand = self.unary()
            return UnaryOp(operator, operand)
        return self.primary()

    def primary(self) -> Expression:
        if self.match("INTEGER"):
            token = self.previous()
            return Literal(int(token.value))
        if self.match("TRUE"):
            token = self.previous()
            return Literal(True)
        if self.match("FALSE"):
            token = self.previous()
            return Literal(False)
        if self.match("IDENTIFIER"):
            identifier = self.previous().value
            # Verifica se o identificador está declarado
            symbol = self.lookup_in_scope(identifier)
            if self.match("LPAREN"):  # Chamada de função
                if not symbol.get("is_function"):
                    raise ParserError(f"'{identifier}' não é uma função.", self.previous())
                args = []
                if not self.check("RPAREN"):
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                self.consume("RPAREN", "Esperado ')' após argumentos da função.")
                return FuncCall(identifier, args)
            else:  # Variável
                if symbol.get("is_function"):
                    raise ParserError(f"'{identifier}' é uma função e não pode ser usado como variável.", self.previous())
                return Identifier(identifier)
        if self.match("LPAREN"):
            expr = self.expression()
            self.consume("RPAREN", "Esperado ')' após expressão.")
            return expr

        raise ParserError("Esperada expressão válida.", self.peek())


    # Métodos auxiliares
    def match(self, *types) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: str, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise ParserError(message, self.peek())

    def consume_type(self) -> str:
        if self.match("INT", "BOOL"):
            return self.previous().type
        raise ParserError("Esperado tipo 'Int' ou 'Bool'.")

    def check(self, type: str) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def peek(self) -> Optional[Token]:
        if self.is_at_end():
            return None
        return self.tokens[self.current]

    def previous(self, steps=1) -> Token:
        return self.tokens[self.current - steps]
