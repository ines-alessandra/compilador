from lexer import Token

Type = str  # Type alias for better readability, can be either "INT" or "BOOL"


class ThreeAddressCodeGenerator:
    def __init__(self):
        self.index = 0
        self.tokens = None
        self.current_token = None
        self.file = open("output.txt", "w")
        self.current_scope = 0
        self.scope = []
        self.labels = 0

    def start(self, tokens: list[Token]):
        self.tokens = tokens
        self.current_token = self.tokens[self.index]

        self.enter_scope()

        self.block()
        while self.tokens:
            self.block()

        self.exit_scope()

        self.file.close()

    def block(self):
        if self.match("IDENTIFIER") and self.match_next("ASSIGN"):
            self.assign()
        elif self.match("PRINT"):
            self.print_declaration()
        elif self.match("FUNCTION"):
            self.function_declaration()
        elif self.match("RETURN"):
            self.return_statement()
        elif self.match("IF"):
            self.if_statement()
        elif self.match("WHILE"):
            self.while_statement()
        elif self.match("IDENTIFIER") and self.match_next("LPAREN"):
            call = self.function_or_procedure_call()
            self.file.write(call)
            self.expect("SEMICOLON")
        elif self.match("IDENTIFIER"):
            self.declaration_without_assign()
        else:
            self.consume_token()

    # <escopo de laço> ::= ( <bloco> | <controle de laço>)+
    def while_scope(self, continue_label, break_label):
        if self.match("PRINT"):
            self.print_declaration()
        elif self.match("FUNCTION"):
            self.function_declaration()
        elif self.match("IF"):
            self.if_statement_while(continue_label, break_label)
        elif self.match("WHILE"):
            self.while_statement()
        elif self.match("BREAK"):
            self.expect("BREAK")
            self.expect("SEMICOLON")
            # Um break gera um salto para fora; portanto, evita-se emitir o goto final
            self.should_fallthrough = False
            self.file.write(f"goto L{break_label}\n")
        elif self.match("CONTINUE"):
            self.expect("CONTINUE")
            self.expect("SEMICOLON")
            # Um continue gera o salto para o topo; desativa o salto automático adicional
            self.should_fallthrough = False
            self.file.write(f"goto L{continue_label}\n")
        elif self.match("IDENTIFIER") and self.match_next("LPAREN"):
            self.function_or_procedure_call()
            self.expect("SEMICOLON")
        elif self.match("IDENTIFIER") and self.match_next("ASSIGN"):
            self.assign()
        else:
            self.consume_token() 

    def assign(self):
        identifier = self.expect("IDENTIFIER")
        self.expect("ASSIGN")

        expression_type = self.expression()

        self.file.write(f"{identifier.value} = {expression_type}\n")

        self.expect("SEMICOLON")

    def print_declaration(self):
        self.expect("PRINT")
        self.expect("LPAREN")
        arguments = []
        if not self.match("RPAREN"):
           arguments = self.argument_list()

        for argument in arguments:
            self.file.write(f"param {argument}\n")
        self.file.write(f"call print,{len(arguments)}\n")

        self.expect("RPAREN")
        self.expect("SEMICOLON")

    def declaration_without_assign(self):
        identifier = self.expect("IDENTIFIER")
        self.expect("SEMICOLON")
        self.file.write(f"{identifier.value} = undefined\n")

    def function_declaration(self):
        self.enter_scope()
        self.expect("FUNCTION")
        identifier = self.expect("IDENTIFIER")
        self.expect("LPAREN")
        params = []

        while not self.match("RPAREN"):
            if not self.match("COMMA"):
                params.append(self.consume_token().value)
            else:
                self.consume_token()
        self.expect("RPAREN")
        self.expect("LBRACE")  # ← importante

        self.file.write(f"\nfunction {identifier.value}({', '.join(params)}):\n")

        while not self.match("RBRACE"):
            self.block()

        self.expect("RBRACE")  # ← isso garante que consome o fim da função

        self.file.write(f"end_function\n\n")
        self.exit_scope()


    def return_statement(self):
        self.expect("RETURN")
        value = self.expression()
        self.expect("SEMICOLON")
        self.file.write(f"return {value}\n")

    # <valor de variável> ::= <identificador> | <inteiro> | <booleano> | <chamada da função/procedimento> | <expressão> | ( <expressão> )
    def variable_value(self) -> Type:

        if self.match("LPAREN"):
            self.expect("LPAREN")
            expression_type = self.expression()
            self.expect("RPAREN")
            return str(expression_type)
        elif self.match("IDENTIFIER"):
            if self.match_next("LPAREN"):
                expression_type = self.function_or_procedure_call()
                temporary = self.get_temporary()
                self.file.write(f"t{temporary} = {expression_type}\n")
                return f"t{temporary}"
            else:
                identifier = self.expect("IDENTIFIER")
                return str(identifier.value)
        elif self.match("INTEGER"):
            value = self.expect("INTEGER")
            return str(value.value)
        elif self.match("TRUE", "FALSE"):
            value = self.expect("TRUE", "FALSE")
            return str(value.value)

    # <chamada da função/procedimento> ::= <identificador>(<argumentos>)
    def function_or_procedure_call(self) -> Type:
        identifier = self.expect("IDENTIFIER")
        self.expect("LPAREN")

        list_of_arguments = []
        if not self.match("RPAREN"):
            list_of_arguments = self.argument_list()

        self.expect("RPAREN")

        for argument in list_of_arguments:
            self.file.write(f"param {argument}\n")

        if len(list_of_arguments) == 0:
            string = f"call {identifier.value}\n"
        else:
            string = f"call {identifier.value},{len(list_of_arguments)}\n"

        return string

    # <argumentos> ::= ε | <valor de variável> | <próx argumentos>
    def argument_list(self) -> list[Type]:
        list_of_arguments = [self.expression()]

        # <próx argumentos> ::= <expressão>,<próx argumentos> | <expressão>
        while self.match("COMMA"):
            self.expect("COMMA")
            list_of_arguments.append(self.expression())

        return list_of_arguments

    def expression(self, return_inverted=False) -> Type:
        #<expressão aritmética> ::= <valor de variável> <operadores aritméticos> <valor de variável>
        expression_type, items = self.arithmetic_expression()
        right_operand_type = None
        operator = None
        #<expressão booleana> ::= <expressão aritmética> <operadores booleanos> <expressão aritmética>
        while self.match("EQUAL", "DIFFERENT", "GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL"):
            operator = self.expect("EQUAL", "DIFFERENT", "GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL").value

            right_operand_type, items = self.arithmetic_expression()

        if right_operand_type is None:
            return expression_type
        else:
            if return_inverted:
                return f"{expression_type} {self.invert_logic_operator(operator)} {right_operand_type}"
            else:
                return f"{expression_type} {operator} {right_operand_type}"

    def arithmetic_expression(self):
        expression_type = self.variable_value()
        right_operand_type = None
        operator = None
        items = []
        items.append(expression_type)
        while self.match("PLUS", "MINUS", "MULTIPLY", "DIVIDE"):
            operator = self.expect("PLUS", "MINUS", "MULTIPLY", "DIVIDE").value
            right_operand_type = self.variable_value()
            items.append(operator)
            items.append(right_operand_type)

        if right_operand_type is None:
            return expression_type, items
        else:
            if len(items) > 3:
                temp = self.generate_three_address_code(items)
                return f"{temp}", items
            else:
                temp = self.get_temporary()
                self.file.write(f"t{temp} = {expression_type} {operator} {right_operand_type}\n")
                return f"t{temp}", items



    # <condicionais> ::= <if> | <if e else>
    def if_statement(self):
        self.expect("IF")
        self.expect("LPAREN")
        expression = self.expression(return_inverted=True)
        label = self.get_label()
        if len(expression.split(" ")) == 1:
            self.file.write(f"if ! {expression} goto L{label}\n")
        else:
            self.file.write(f"if {expression} goto L{label}\n")
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.conditional_scope()
        self.expect("RBRACE")

        end_label = None
        if self.match("ELSE"):
            end_label = self.get_label()
            self.file.write(f"goto L{end_label}\n")
            self.file.write(f"L{label}:\n")
            self.expect("ELSE")
            self.expect("LBRACE")
            self.conditional_scope()
            self.expect("RBRACE")

        if end_label is not None:
            self.file.write(f"L{end_label}:\n")
        else:
            self.file.write(f"L{label}:\n")



    # (<bloco>)+
    def conditional_scope(self):
        # REMOVE THIS IF ERROR WITH SCOPES
        self.enter_scope()

        while not self.match("RBRACE") and not self.match("ELSE"):
            self.block()
        # REMOVE THIS IF ERROR WITH SCOPES
        self.exit_scope()

    # <laço> ::= while (<expressão booleana>) {
    #       <escopo do laço>
    # }

    def while_statement(self):
        self.expect("WHILE")
        self.expect("LPAREN")
        continue_label = self.get_label()
        break_label = self.get_label()
        # Inicializa a flag como True; se o loop emitir um salto (continue/break), ela será setada para False
        self.should_fallthrough = True

        expression = self.expression(return_inverted=True)
        self.file.write(f"L{continue_label}:\n")
        if len(expression.split(" ")) == 1:
            self.file.write(f"if ! {expression} goto L{break_label}\n")
        else:
            self.file.write(f"if {expression} goto L{break_label}\n")
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.loop_scope(continue_label, break_label)
        self.expect("RBRACE")
        
        # Somente se nenhuma instrução no corpo gerou um salto explícito,
        # emitimos o goto para voltar à verificação da condição.
        if self.should_fallthrough:
            self.file.write(f"goto L{continue_label}\n")
        self.file.write(f"L{break_label}:\n")

    # <escopo do laço>
    def loop_scope(self, continue_label, break_label):
        self.enter_scope()

        while not self.match("RBRACE"):
            self.while_scope(continue_label, break_label)

        self.exit_scope()



    # This is the same as the if_statment, but it uses the conditional_scope_while instead of block to allow break and continue;
    def if_statement_while(self, continue_label, break_label):
        self.expect("IF")
        self.expect("LPAREN")
        expression = self.expression(return_inverted=True)
        label = self.get_label()
        if len(expression.split(" ")) == 1:
            self.file.write(f"if ! {expression} goto L{label}\n")
        else:
            self.file.write(f"if {expression} goto L{label}\n")
        self.expect("RPAREN")
        self.expect("LBRACE")
        self.conditional_scope_while(continue_label, break_label)
        self.expect("RBRACE")
        self.file.write(f"L{label}:\n")
        if self.current_token is not None and self.match("ELSE"):
            self.expect("ELSE")
            self.expect("LBRACE")
            self.conditional_scope_while(continue_label, break_label)
            self.expect("RBRACE")

    # This is the same as the conditional_scope, but it uses the while_scope instead of block to allow break and continue;
    def conditional_scope_while(self, continue_label, break_label):
        self.enter_scope()

        while not self.match("RBRACE") and not self.match("ELSE"):
            self.while_scope(continue_label, break_label)

        self.exit_scope()


    def precedence(self, op):
        if op == '+' or op == '-':
            return 1
        if op == '*' or op == '/':
            return 2
        return 0

    """
    1 - Ler a expressão da esquerda pra direita. 
    2 - Se o caracter lido for operando adiciona na pilha. 
        Caso contrário
        
    3 - Se a precedencia do operador lido for menor que a precedencia do operador no topo da pilha, adicionar na pilha.
    4 - Caso contrário, remova do topo da pilha os operadores que são maiores ou iguais de procedência que o operador lido.
        Adicione cada um que foi removido na saída.

    5 - Repetir passos acima até que termine a expressão. 
    6 - Remova todos os itens da pilha até que ela fique vazia e adicione a saída
    """
    def infix_to_postfix(self, expression):
        stack = []
        output = []
        for char in expression:
            if char.isalnum():  # if the character is an operand
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                while stack and self.precedence(stack[-1]) >= self.precedence(char):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())
        return output

    """
    def generate_three_address_code(expression):
    postfix = infix_to_postfix(expression)
    
    stack = []

    for char in postfix:
        if é_operando(char):
            empilha na pilha
        else:
            # Se o caractere é um operador:
            
            # Desempilha os dois operandos necessários para a operação
           
            # Escreve a instrução de código de três endereços no arquivo
            
            # Empilha o nome da variável temporária
    
    Retorna o último elemento da pilha, que é o resultado final    
    """
    def generate_three_address_code(self, expression):
        postfix = self.infix_to_postfix(expression)
        stack = []
        for char in postfix:
            if char.isalnum():  # if the character is an operand
                stack.append(char)
            else:
                right = stack.pop()
                left = stack.pop()
                temp_var = f"t{self.get_temporary()}"
                self.file.write(f"{temp_var} = {left} {char} {right}\n")
                stack.append(temp_var)
        return stack[-1]

    def invert_logic_operator(self, operator):
        if operator == "==":
            return "!="
        elif operator == "!=":
            return "=="
        elif operator == ">":
            return "<="
        elif operator == "<":
            return ">="
        elif operator == ">=":
            return "<"
        elif operator == "<=":
            return ">"
        elif operator == "true":
            return "false"
        elif operator == "false":
            return "true"

    def get_label(self):
        label = self.labels
        self.labels += 1
        return label

    def get_temporary(self):
        temporary = self.scope[self.current_scope - 1][0]
        self.scope[self.current_scope - 1][0] += 1
        return temporary

    def enter_scope(self):
        self.current_scope += 1
        self.scope.insert(self.current_scope, [0])

    def exit_scope(self):
        self.current_scope -= 1
        self.scope.pop()

    def consume_token(self):
        token = self.tokens.pop(0)
        if self.tokens:
            self.current_token = self.tokens[0]
        else:
            self.current_token = None
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

    def match_next(self, *expected_token_types):
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index + 1].token_type in expected_token_types
        else:
            return False

    def match(self, *expected_token_types):
        token = self.current_token
        return token.token_type in expected_token_types
