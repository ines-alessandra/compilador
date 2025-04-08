from lexer import Token
import json

Type = str  # Type alias for better readability, can be either "INT" or "BOOL"


class SemanticError(Exception):
    pass


FUNCTION = "FUNCTION"
VARIABLE = "VARIABLE"


class Parser:
    """
    Syntactic and semantic analysis of the program. And also create three address code.
    """

    def __init__(self):
        self.index = 0
        self.tokens = None
        self.current_token = None
        self.current_scope = -1
        self.symbol_table = []
        self.instructions = []

    def parse(self, tokens: list[Token]):
        self.tokens = tokens
        self.current_token = self.tokens[self.index]
        self.program()

        if self.current_token is not None:
            self.error()

    # <escopo de programa> ::= (<bloco>)*
    def program(self):
        self.enter_scope()

        self.block()
        while self.current_token is not None:
            self.block()

        self.exit_scope()

    #<bloco> :== <declaração de variável> | <imprimir> | <declaração de função/procedimento> | <condicionais> | <laço>  | <chamada da função/procedimento> |  <atribuição>
    def block(self):
        if self.match("CONST", "VARIABLE"):
            self.declaration_and_assignment()
        elif self.match("PRINT"):
            self.print_statement()
        elif self.match("FUNCTION"):
            self.declaration_of_function_or_procedure()
        elif self.match("IF"):
            self.if_statement()
        elif self.match("WHILE"):
            self.while_statement()
        elif self.match("IDENTIFIER") and self.match_next("LPAREN"):
            self.function_or_procedure_call()
            self.expect("SEMICOLON")
        elif self.match("IDENTIFIER") and self.match_next("ASSIGN"):
            self.assignment_statement()
        #else:
        #    self.variable_value()
        #    self.expect("SEMICOLON")
        else:
            self.error()

    #<escopo de laço> ::= ( <bloco> | <controle de laço>)+
    def while_scope(self):
        if self.match("CONST", "VARIABLE"):
            self.declaration_and_assignment()
        elif self.match("PRINT"):
            self.print_statement()
        elif self.match("FUNCTION"):
            self.declaration_of_function_or_procedure()
        elif self.match("IF"):
            self.if_statement_while()
        elif self.match("WHILE"):
            self.while_statement()
        elif self.match("BREAK"):
            self.expect("BREAK")
            self.expect("SEMICOLON")
        elif self.match("CONTINUE"):
            self.expect("CONTINUE")
            self.expect("SEMICOLON")
        elif self.match("IDENTIFIER") and self.match_next("LPAREN"):
            self.function_or_procedure_call()
            self.expect("SEMICOLON")
        elif self.match("IDENTIFIER") and self.match_next("ASSIGN"):
            self.assignment_statement()
            #else:
            #    self.variable_value()
            #    self.expect("SEMICOLON")
        else:
            self.error()

    #<escopo de função> ::= (<bloco><retorno>)+
    def function_or_procedure_scope(self):
        while not self.match("RBRACE", "RETURN"):
            self.block()

    #<declaração de variável> ::= <tipo de variável> <identificador> : <tipo> ; | <tipo de variável> <identificador> :  <tipo> = <valor de variável> ;
    def declaration_and_assignment(self):
        identifier_type = self.expect("CONST", "VARIABLE")
        identifier = self.expect("IDENTIFIER")
        self.expect("COLON")
        variable_type = self.expect("INT", "BOOL")

        self.check_already_declared_variable(VARIABLE, identifier)

        if self.match("ASSIGN"):
            self.expect("ASSIGN")
            expression_type = self.expression()
            self.check_types(variable_type.token_type, expression_type)

        self.expect("SEMICOLON")

        self.symbol_table[self.current_scope][identifier] = {
            "const_or_val": identifier_type.token_type,
            "fun_or_var": VARIABLE,
            "variable_type": variable_type,
            "scope": self.current_scope,
        }

    # <atribuição> ::= <identificador> = <valor de variável> ;
    def assignment_statement(self):
        identifier = self.expect("IDENTIFIER")
        variable_type = self.get_variable_type(VARIABLE, identifier)
        identifier_type = self.get_identifier_type(VARIABLE, identifier)

        self.check_assignment(identifier_type, identifier)

        self.expect("ASSIGN")
        expression_type = self.expression()
        self.check_types(variable_type, expression_type)
        self.expect("SEMICOLON")

    # <valor de variável> ::= <identificador> | <inteiro> | <booleano> | <chamada da função/procedimento> | <expressão> | ( <expressão> )
    def variable_value(self) -> Type:
        expression_type = None

        if self.match("LPAREN"):
            self.expect("LPAREN")
            expression_type = self.expression()
            self.expect("RPAREN")
        elif self.match("IDENTIFIER"):
            if self.match_next("LPAREN"):
                expression_type = self.function_or_procedure_call()
            else:
                identifier = self.expect("IDENTIFIER")
                expression_type = self.get_variable_type(VARIABLE, identifier)

        elif self.match("INTEGER"):
            self.expect("INTEGER")
            expression_type = "INT"
        elif self.match("TRUE", "FALSE"):
            self.expect("TRUE", "FALSE")
            expression_type = "BOOL"
        else:
            self.error()

        return expression_type

    #<expressão> :==  <expressão booleana> | <expressão aritmética>
    def expression(self) -> Type:
        #<expressão aritmética> ::= <valor de variável> <operadores aritméticos> <valor de variável>
        expression_type = self.arithmetic_expression()
        #<expressão booleana> ::= <expressão aritmética> <operadores booleanos> <expressão aritmética>
        while self.match("EQUAL", "DIFFERENT", "GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL"):
            operator = self.expect("EQUAL", "DIFFERENT", "GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL")

            right_operand_type = self.arithmetic_expression(previous_operand_type="BOOL")

            if expression_type != right_operand_type:
                raise SemanticError(
                    f"Type mismatch: Cannot perform {operator} operation between {expression_type} and "
                    f"{right_operand_type} at line {self.current_token.line}"
                )

            expression_type = "BOOL"

        return expression_type

    #<expressão aritmética> ::= <valor de variável> | <valor de variável> <operadores aritméticos> <valor de variável>
    def arithmetic_expression(self, previous_operand_type="") -> Type:
        expression_type = self.variable_value()
        while self.match("PLUS", "MINUS", "MULTIPLY", "DIVIDE"):
            operator = self.expect("PLUS", "MINUS", "MULTIPLY", "DIVIDE")
            #if operator.token_type == "DIVIDE":
            #    raise SemanticError(
            #        f"Cannot perform division operation at line {operator.line}, float type not supported"
            #    )
            right_operand_type = self.variable_value()

            if previous_operand_type != "":
                if previous_operand_type != expression_type:
                    raise SemanticError(
                        f"Type mismatch: Cannot perform {operator} operation between {previous_operand_type} and "
                        f"{expression_type} at line {self.current_token.line}"
                    )

            if expression_type != right_operand_type:
                raise SemanticError(
                    f"Type mismatch: Cannot perform {operator} operation between {expression_type} and "
                    f"{right_operand_type} at line {self.current_token.line}"
                )

            expression_type = "INT"

        return expression_type

    #<imprimir> ::= print(<argumentos>);
    def print_statement(self):
        self.expect("PRINT")
        self.expect("LPAREN")
        if self.current_token.token_type != "RPAREN":
            self.argument_list()
        else:
            raise SemanticError(
                f"Cannot print empty list at line {self.current_token.line}"
            )

        self.expect("RPAREN")
        self.expect("SEMICOLON")

    #<retorno> ::= return <valor de variável> ;
    def return_statement(self, variable_type):
        self.expect("RETURN")
        right_type = self.expression()
        if variable_type.token_type != right_type:
            raise SemanticError(
                f"Type mismatch: Cannot return {right_type} in function with return type {variable_type.token_type} at line {self.current_token.line}"
            )
        self.expect("SEMICOLON")

    #<declaração de função/procedimento> :== <função> | <procedimento>
    def declaration_of_function_or_procedure(self):
        self.expect("FUNCTION")
        identifier = self.expect("IDENTIFIER")

        self.check_already_declared_variable(FUNCTION, identifier)

        self.enter_scope()

        self.expect("LPAREN")

        list_of_parameters = []
        if not self.match("RPAREN"):
            list_of_parameters = self.parameters()

        self.expect("RPAREN")

        #<função> ::= function <identificador> (<parâmetros>) : <tipo> {
        #           <escopo de função>
        #}
        if self.match("COLON"):
            self.expect("COLON")
            variable_type = self.expect("INT", "BOOL")
            self.expect("LBRACE")
            self.function_or_procedure_scope()
            self.return_statement(variable_type)
        #<procedimento> ::= function <identificador> (<parâmetros>) {
        #       (<bloco>)+
        #}
        else:
            variable_type = None
            self.expect("LBRACE")
            self.function_or_procedure_scope()

        self.expect("RBRACE")

        self.symbol_table[self.current_scope - 1][identifier] = {
            "const_or_val": None,
            "fun_or_var": FUNCTION,
            "variable_type": variable_type,
            "scope": self.current_scope - 1,
            "parameters": list_of_parameters,
        }

        self.exit_scope()

    # <parâmetros> ::= ε | <identificador> <símbolo de tipo> <tipo>  | <n parâmetros>
    def parameters(self) -> list[Type]:
        list_of_parameters = []
        identifier = self.expect("IDENTIFIER")
        self.expect("COLON")
        variable_type = self.expect("INT", "BOOL")
        list_of_parameters.append(variable_type.token_type)

        self.symbol_table[self.current_scope][identifier] = {
            "const_or_val": "VARIABLE",
            "fun_or_var": VARIABLE,
            "variable_type": variable_type,
            "scope": self.current_scope,
        }

        #<n parâmetros> ::= <identificador> : <tipo>,<n parâmetros> | <identificador> : <tipo>
        while self.match("COMMA"):
            self.expect("COMMA")
            identifier = self.expect("IDENTIFIER")
            self.expect("COLON")
            variable_type = self.expect("INT", "BOOL")
            list_of_parameters.append(variable_type.token_type)
            self.symbol_table[self.current_scope][identifier] = {
                "const_or_val": "VARIABLE",
                "fun_or_var": VARIABLE,
                "variable_type": variable_type,
                "scope": self.current_scope,
            }

        return list_of_parameters

    #<chamada da função/procedimento> ::= <identificador>(<argumentos>)
    def function_or_procedure_call(self) -> Type:
        identifier = self.expect("IDENTIFIER")

        list_of_parameters = None
        for scope in self.symbol_table:
            for token in scope.keys():
                if token.value == identifier.value and scope[token]["fun_or_var"] == FUNCTION:
                    list_of_parameters = scope[token]["parameters"]
                    break

        if list_of_parameters is None:
            raise SemanticError(
                f"Function '{identifier.value}' in line {identifier.line} not declared"
            )

        self.expect("LPAREN")

        list_of_arguments = []
        if not self.match("RPAREN"):
            list_of_arguments = self.argument_list()

        self.expect("RPAREN")

        if len(list_of_parameters) != len(list_of_arguments):
            raise SemanticError(
                f"Invalid number of arguments in function '{identifier.value}' at line {identifier.line}. "
                f"Expected {len(list_of_parameters)} parameters, found {len(list_of_arguments)}"
            )

        for i in range(len(list_of_parameters)):
            if list_of_parameters[i] != list_of_arguments[i]:
                raise SemanticError(
                    f"Type mismatch: Cannot assign {list_of_arguments[i]} to {list_of_parameters[i]} "
                    f"parameter in function '{identifier.value}' at line {identifier.line}"
                )

        expression_type = self.get_variable_type(FUNCTION, identifier)

        return expression_type

    #<argumentos> ::= ε | <valor de variável> | <próx argumentos>
    def argument_list(self) -> list[Type]:
        list_of_arguments = [self.expression()]

        #<próx argumentos> ::= <expressão>,<próx argumentos> | <expressão>
        while self.match("COMMA"):
            self.expect("COMMA")
            list_of_arguments.append(self.expression())

        return list_of_arguments

    #<condicionais> ::= <if> | <if e else>
    def if_statement(self):
        #<if> ::= if (<expressão booleana>) {
        #   (<bloco>)+
        #}
        self.expect("IF")
        self.expect("LPAREN")
        expression_type = self.expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in IF statement at line {self.current_token.line}"
            )
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.conditional_scope()
        self.expect("RBRACE")

        #<if e else> :== if (<expressão booleana>) {
        #        (<bloco>)+
        #}
        #else {
        #    (<bloco>)+
        #}
        if self.current_token is not None and self.match("ELSE"):
            self.expect("ELSE")
            self.expect("LBRACE")
            self.conditional_scope()
            self.expect("RBRACE")

    # (<bloco>)+
    def conditional_scope(self):
        # REMOVE THIS IF ERROR WITH SCOPES
        self.enter_scope()

        while not self.match("RBRACE") and not self.match("ELSE"):
            self.block()
        # REMOVE THIS IF ERROR WITH SCOPES
        self.exit_scope()

    #<laço> ::= while (<expressão booleana>) {
    #       <escopo do laço>
    #}

    def while_statement(self):
        self.expect("WHILE")
        self.expect("LPAREN")
        expression_type = self.expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in WHILE statement at line {self.current_token.line}"
            )
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.loop_scope()
        self.expect("RBRACE")

    #<escopo do laço>
    def loop_scope(self):
        self.enter_scope()

        while not self.match("RBRACE"):
            self.while_scope()

        self.exit_scope()

    # This is the same as the if_statment, but it uses the conditional_scope_while instead of block to allow break and continue;
    def if_statement_while(self):
        self.expect("IF")
        self.expect("LPAREN")
        expression_type = self.expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in IF statement at line {self.current_token.line}"
            )
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.conditional_scope_while()
        self.expect("RBRACE")
        if self.current_token is not None and self.match("ELSE"):
            self.expect("ELSE")
            self.expect("LBRACE")
            self.conditional_scope_while()
            self.expect("RBRACE")

    # This is the same as the conditional_scope, but it uses the while_scope instead of block to allow break and continue;
    def conditional_scope_while(self):
        self.enter_scope()

        while not self.match("RBRACE") and not self.match("ELSE"):
            self.while_scope()

        self.exit_scope()

    ############################################ UTILS ################################################################

    def check_already_declared_variable(self, identifier_type, identifier: Token):
        # check if the variable has already been declared in the current scope or in the parent scopes
        for scope in reversed(self.symbol_table):
            for token in scope.keys():
                if (token.value == identifier.value and scope[token]["fun_or_var"] == identifier_type and
                        scope[token]["scope"] == self.current_scope):
                    raise SemanticError(
                        f"{identifier_type} '{identifier.value}' in line {identifier.line} "
                        f"already declared in line {token.line}"
                    )

    def check_assignment(self, identifier_type, identifier: Token):
        if identifier_type is None or identifier_type == "CONST":
            raise SemanticError(
                f"Variable {identifier} at line {identifier.line} cannot be assigned to a value because its constant type"
            )

    def consume_token(self):
        token = self.current_token
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None
        if token.token_type not in ["CONST", "VARIABLE", "COLON", "INT", "BOOL"]:
            self.instructions.append(token)
        return token

    def expect(self, *expected_token_types):
        if self.current_token:
            if self.current_token.token_type not in expected_token_types:
                raise SyntaxError(
                    f"Expected one of {expected_token_types} at line {self.current_token.line}, but found {self.current_token.token_type}")
            return self.consume_token()
        else:
            raise SyntaxError(
                f"Expected {expected_token_types}, but found EOF at line {self.tokens[-1].line}"
            )

    def get_variable_type(self, identifier_type, variable_token: Token) -> Type | None:
        for scope in reversed(self.symbol_table):
            for token in scope.keys():
                if token.value == variable_token.value and scope[token]["fun_or_var"] == identifier_type:
                    if scope[token]["variable_type"] == None:
                        return None
                    return scope[token]["variable_type"].token_type

        raise SemanticError(
            f"Variable '{variable_token.value}' used before declaration at line {variable_token.line}"
        )

    def get_identifier_type(self, identifier_type, variable_token: Token) -> Type:
        for scope in reversed(self.symbol_table):
            for token in scope.keys():
                if token.value == variable_token.value and scope[token]["fun_or_var"] == identifier_type:
                    return scope[token]["const_or_val"]

        raise SemanticError(
            f"Variable '{variable_token.value}' used before declaration at line {variable_token.line}"
        )

    @staticmethod
    def check_types(left_type: Type, right_type: Type):
        if left_type == "INT" and right_type != "INT":
            raise SemanticError(
                f"Type mismatch: Cannot assign {right_type} to INT variable"
            )
        elif left_type == "BOOL" and right_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot assign {right_type} to BOOL variable"
            )

    def error(self):
        raise SyntaxError(
            f"Syntax error at line {self.current_token.line} unexpected token {self.current_token}"
        )

    def enter_scope(self):
        self.current_scope += 1
        self.symbol_table.insert(self.current_scope, {})

    def exit_scope(self):
        self.symbol_table.pop()
        self.current_scope -= 1

    def match_next(self, *expected_token_types):
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index + 1].token_type in expected_token_types
        else:
            return False

    def match(self, *expected_token_types):
        token = self.current_token
        return token.token_type in expected_token_types
    def to_dict(self, node):
        """Converte um nó da AST em um dicionário serializável."""
        if isinstance(node, dict):
            return {k: self.to_dict(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [self.to_dict(item) for item in node]
        elif hasattr(node, '__dict__'):
            # Para objetos, pega seus atributos
            result = {}
            for key, value in node.__dict__.items():
                # Ignora atributos internos ou que não queremos serializar
                if not key.startswith('_'):
                    result[key] = self.to_dict(value)
            return result
        else:
            # Tipos básicos (str, int, float, bool, None)
            return node

    def save_ast_to_file(self, ast, filename):
        """Salva a AST em um arquivo JSON."""
        ast_dict = self.to_dict(ast)
        with open(filename, 'w') as f:
            json.dump(ast_dict, f, indent=2, ensure_ascii=False)
