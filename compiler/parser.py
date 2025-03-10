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
            return f"[Linha {self.token.line}] Erro: {self.message} (Token atual: {self.token.value})"
        return f"Erro: {self.message}"

# Nó base da AST com informação de posição
class ASTNode:
    def __init__(self, line=None):
        self.line = line

class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode], line=None):
        super().__init__(line)
        self.declarations = declarations

class VarDecl(ASTNode):
    def __init__(self, is_const: bool, name: str, var_type: str, initializer: ASTNode, line=None):
        super().__init__(line)
        self.is_const = is_const
        self.name = name
        self.var_type = var_type
        self.initializer = initializer

class FuncDecl(ASTNode):
    def __init__(self, name: str, params: List[tuple], return_type: str = "Unit", body: ASTNode = None, line=None):
        super().__init__(line)
        self.name = name
        self.params = params  # Lista de tuplas (nome, tipo, linha)
        self.return_type = return_type
        self.body = body

class Block(ASTNode):
    def __init__(self, declarations: List[ASTNode], line=None):
        super().__init__(line)
        self.declarations = declarations

class Assignment(ASTNode):
    def __init__(self, name: str, value: ASTNode, line=None):
        super().__init__(line)
        self.name = name
        self.value = value

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: Optional[ASTNode], line=None):
        super().__init__(line)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode, line=None):
        super().__init__(line)
        self.condition = condition
        self.body = body

class ReturnStatement(ASTNode):
    def __init__(self, value: ASTNode, line=None):
        super().__init__(line)
        self.value = value

class BreakStatement(ASTNode):
    def __init__(self, line=None):
        super().__init__(line)

class ContinueStatement(ASTNode):
    def __init__(self, line=None):
        super().__init__(line)

class PrintStatement(ASTNode):
    def __init__(self, value: ASTNode, line=None):
        super().__init__(line)
        self.value = value

class Expression(ASTNode):
    pass

class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression, line=None):
        super().__init__(line)
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(Expression):
    def __init__(self, operator: str, operand: Expression, line=None):
        super().__init__(line)
        self.operator = operator
        self.operand = operand

class Literal(Expression):
    def __init__(self, value, line=None):
        super().__init__(line)
        self.value = value

class Identifier(Expression):
    def __init__(self, name: str, line=None):
        super().__init__(line)
        self.name = name

class FuncCall(Expression):
    def __init__(self, name: str, args: List[Expression], line=None):
        super().__init__(line)
        self.name = name
        self.args = args

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.scope_stack = [{}]
        self.loop_depth = 0  # Controla aninhamento de loops
        self.in_function = False  # Indica se estamos dentro de uma função

    def parse(self) -> Program:
        declarations = []
        while not self.is_at_end():
            try:
                decl = self.declaration()
                if decl is not None:
                    declarations.append(decl)
            except ParserError as e:
                print(e)
                self.synchronize()
        return Program(declarations, line=declarations[0].line if declarations else None)

    def synchronize(self):
        # Avança tokens até encontrar um ponto de sincronização: ';' ou '}'
        self.advance()
        while not self.is_at_end():
            if self.previous().type == "SEMICOLON":
                return
            if self.peek() and self.peek().type == "RBRACE":
                return
            self.advance()

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

    def declaration(self) -> Optional[ASTNode]:
        if self.match("VARIABLE"):  # 'val'
            return self.var_decl(is_const=False)
        if self.match("CONST"):  # 'const'
            return self.var_decl(is_const=True)
        if self.match("FUNCTION"):  # 'fun'
            return self.func_decl()
        return self.statement()

    def var_decl(self, is_const: bool) -> VarDecl:
        name_token = self.consume("IDENTIFIER", "Esperado nome da variável.")
        self.consume("COLON", "Esperado ':' após o nome da variável.")
        var_type = self.consume_type()
        self.consume("ASSIGN", "Esperado '=' na declaração da variável.")
        initializer = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após a declaração da variável.")
        
        self.add_to_scope(name_token.value, var_type, is_const)
        
        return VarDecl(is_const, name_token.value, var_type, initializer, line=name_token.line)

    def func_decl(self) -> FuncDecl:
        name_token = self.consume("IDENTIFIER", "Esperado nome da função.")
        self.consume("LPAREN", "Esperado '(' após o nome da função.")
        
        params = []
        if not self.check("RPAREN"):
            params.append(self.parameter())
            while self.match("COMMA"):
                params.append(self.parameter())
        self.consume("RPAREN", "Esperado ')' após parâmetros da função.")
        
        if self.match("COLON"):
            return_type = self.consume_type()
        else:
            return_type = "Unit"
        
        self.add_to_scope(name_token.value, is_function=True, params=params, return_type=return_type)
        
        self.enter_scope()
        for param_name, param_type, _ in params:
            self.add_to_scope(param_name, var_type=param_type)
        
        prev_in_function = self.in_function
        self.in_function = True  # Entramos no escopo de uma função
        body = self.block()
        self.in_function = prev_in_function
        
        return FuncDecl(name_token.value, params, return_type, body, line=name_token.line)

    def parameter(self) -> tuple:
        name_token = self.consume("IDENTIFIER", "Esperado nome do parâmetro.")
        self.consume("COLON", "Esperado ':' após o nome do parâmetro.")
        param_type = self.consume_type()
        return (name_token.value, param_type, name_token.line)

    def block(self) -> Block:
        lbrace_token = self.consume("LBRACE", "Esperado '{' para iniciar o bloco.")
        self.enter_scope() 
        declarations = []
        while not self.check("RBRACE") and not self.is_at_end():
            try:
                decl = self.declaration()
                if decl is not None:
                    declarations.append(decl)
            except ParserError as e:
                print(e)
                self.synchronize()
        self.consume("RBRACE", "Esperado '}' para fechar o bloco.")
        self.exit_scope()
        return Block(declarations, line=lbrace_token.line)

    def statement(self) -> ASTNode:
        if self.match("IF"):
            return self.if_statement()
        if self.match("WHILE"):
            return self.while_statement()
        if self.match("RETURN"):
            return self.return_statement()
        if self.match("BREAK"):
            if self.loop_depth == 0:
                raise ParserError("Comando 'break' usado fora de um loop.", self.peek())
            token = self.previous()
            self.consume("SEMICOLON", "Esperado ';' após 'break'.")
            return BreakStatement(line=token.line)
        if self.match("CONTINUE"):
            if self.loop_depth == 0:
                raise ParserError("Comando 'continue' usado fora de um loop.", self.peek())
            token = self.previous()
            self.consume("SEMICOLON", "Esperado ';' após 'continue'.")
            return ContinueStatement(line=token.line)
        if self.match("PRINT"):
            return self.print_statement()
        
        if self.peek() and self.peek().type == "IDENTIFIER":
            if (self.current + 1) < len(self.tokens) and self.tokens[self.current + 1].type == "ASSIGN":
                return self.assignment()
            else:
                return self.expression_statement()
        
        raise ParserError("Esperado declaração ou instrução.", self.peek())

    def expression_statement(self) -> ASTNode:
        expr = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após expressão.")
        return expr

    def if_statement(self) -> IfStatement:
        token = self.previous()  # token 'if'
        self.consume("LPAREN", "Esperado '(' após 'if'.")
        condition = self.expression()
        self.consume("RPAREN", "Esperado ')' após condição do 'if'.")
        then_branch = self.block()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.block()
        return IfStatement(condition, then_branch, else_branch, line=token.line)

    def while_statement(self) -> WhileStatement:
        token = self.previous()  # token 'while'
        self.consume("LPAREN", "Esperado '(' após 'while'.")
        condition = self.expression()
        self.consume("RPAREN", "Esperado ')' após condição do 'while'.")
        self.loop_depth += 1
        body = self.block()
        self.loop_depth -= 1
        return WhileStatement(condition, body, line=token.line)

    def return_statement(self) -> ReturnStatement:
        token = self.previous()  # token 'return'
        if not self.in_function:
            raise ParserError("Comando 'return' usado fora de função.", token)
        value = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após 'return'.")
        return ReturnStatement(value, line=token.line)

    def print_statement(self) -> PrintStatement:
        token = self.previous()  # token 'print'
        self.consume("LPAREN", "Esperado '(' após 'print'.")
        value = self.expression()
        self.consume("RPAREN", "Esperado ')' após expressão do 'print'.")
        self.consume("SEMICOLON", "Esperado ';' após 'print'.")
        return PrintStatement(value, line=token.line)

    def assignment(self) -> Assignment:
        name_token = self.consume("IDENTIFIER", "Esperado um identificador para atribuição.")
        self.lookup_in_scope(name_token.value)
        self.consume("ASSIGN", "Esperado '=' em atribuição.")
        value = self.expression()
        self.consume("SEMICOLON", "Esperado ';' após atribuição.")
        return Assignment(name_token.value, value, line=name_token.line)

    def expression(self) -> Expression:
        return self.equality()

    def equality(self) -> Expression:
        expr = self.comparison()
        while self.match("EQUAL", "DIFFERENT"):
            operator = self.previous().type
            right = self.comparison()
            expr = BinaryOp(expr, operator, right, line=self.previous().line)
        return expr

    def comparison(self) -> Expression:
        expr = self.term()
        while self.match("GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL"):
            operator = self.previous().type
            right = self.term()
            expr = BinaryOp(expr, operator, right, line=self.previous().line)
        return expr

    def term(self) -> Expression:
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            operator = self.previous().type
            right = self.factor()
            expr = BinaryOp(expr, operator, right, line=self.previous().line)
        return expr

    def factor(self) -> Expression:
        expr = self.unary()
        while self.match("MULTIPLY", "DIVIDE"):
            operator = self.previous().type
            right = self.unary()
            expr = BinaryOp(expr, operator, right, line=self.previous().line)
        return expr

    def unary(self) -> Expression:
        if self.match("MINUS", "NOT"):
            operator = self.previous().type
            operand = self.unary()
            return UnaryOp(operator, operand, line=self.previous().line)
        return self.primary()

    def primary(self) -> Expression:
        if self.match("INTEGER"):
            token = self.previous()
            return Literal(int(token.value), line=token.line)
        if self.match("TRUE"):
            token = self.previous()
            return Literal(True, line=token.line)
        if self.match("FALSE"):
            token = self.previous()
            return Literal(False, line=token.line)
        if self.match("IDENTIFIER"):
            token = self.previous()
            identifier = token.value
            symbol = self.lookup_in_scope(identifier)
            if self.match("LPAREN"):
                if not symbol.get("is_function"):
                    raise ParserError(f"'{identifier}' não é uma função.", token)
                args = []
                if not self.check("RPAREN"):
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                self.consume("RPAREN", "Esperado ')' após argumentos da função.")
                return FuncCall(identifier, args, line=token.line)
            else:
                if symbol.get("is_function"):
                    raise ParserError(f"'{identifier}' é uma função e não pode ser usado como variável.", token)
                return Identifier(identifier, line=token.line)
        if self.match("LPAREN"):
            token = self.previous()
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
        raise ParserError("Esperado tipo 'Int' ou 'Bool'.", self.peek())

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
