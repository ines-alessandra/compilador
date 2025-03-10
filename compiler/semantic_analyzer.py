# semantic_analyzer.py

from parser import (
    Program, VarDecl, FuncDecl, Block, Assignment, IfStatement,
    WhileStatement, ReturnStatement, BreakStatement, ContinueStatement,
    PrintStatement, BinaryOp, UnaryOp, Literal, Identifier, FuncCall
)

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.scope_stack = [{}]

    def analyze(self, node):
        if isinstance(node, Program):
            self.enter_scope()
            for decl in node.declarations:
                self.analyze(decl)
            self.exit_scope()
        elif isinstance(node, VarDecl):
            self.declare_variable(node)
            expr_type = self.analyze(node.initializer)
            if expr_type != node.var_type:
                raise SemanticError(
                    f"Type mismatch na declaração da variável '{node.name}'. "
                    f"Esperado '{node.var_type}', mas foi encontrado '{expr_type}'."
                )
        elif isinstance(node, Assignment):
            var_type = self.lookup_variable(node.name)
            expr_type = self.analyze(node.value)
            if var_type != expr_type:
                raise SemanticError(
                    f"Type mismatch na atribuição para '{node.name}'. "
                    f"Variável do tipo '{var_type}' não pode receber valor do tipo '{expr_type}'."
                )
        elif isinstance(node, FuncDecl):
            self.declare_function(node)
            self.enter_scope()
            # Agora desempacotamos três valores: nome, tipo e linha
            for param_name, param_type, param_line in node.params:
                self.current_scope()[param_name] = {"type": param_type, "is_const": False}
            body_type = self.analyze(node.body)
            if node.return_type != "Unit" and body_type != node.return_type:
                raise SemanticError(
                    f"Type mismatch na função '{node.name}'. "
                    f"Esperado retorno '{node.return_type}', mas o corpo retorna '{body_type}'."
                )
            self.exit_scope()
        elif isinstance(node, Block):
            self.enter_scope()
            ret_type = None
            for decl in node.declarations:
                result = self.analyze(decl)
                if isinstance(decl, ReturnStatement):
                    ret_type = result
            self.exit_scope()
            return ret_type
        elif isinstance(node, IfStatement):
            cond_type = self.analyze(node.condition)
            if cond_type != "BOOL":
                raise SemanticError("A condição do 'if' deve ser do tipo BOOL.")
            self.analyze(node.then_branch)
            if node.else_branch:
                self.analyze(node.else_branch)
        elif isinstance(node, WhileStatement):
            cond_type = self.analyze(node.condition)
            if cond_type != "BOOL":
                raise SemanticError("A condição do 'while' deve ser do tipo BOOL.")
            self.analyze(node.body)
        elif isinstance(node, ReturnStatement):
            return self.analyze(node.value)
        elif isinstance(node, PrintStatement):
            return self.analyze(node.value)
        elif isinstance(node, BinaryOp):
            left_type = self.analyze(node.left)
            right_type = self.analyze(node.right)
            if node.operator in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE"]:
                if left_type != "INT" or right_type != "INT":
                    raise SemanticError("Operadores aritméticos só aceitam operandos do tipo INT.")
                return "INT"
            elif node.operator in ["EQUAL", "DIFFERENT", "GREATER", "GREATER_OR_EQUAL", "LESS", "LESS_OR_EQUAL"]:
                if left_type != right_type:
                    raise SemanticError("Operadores relacionais exigem que os operandos sejam do mesmo tipo.")
                return "BOOL"
            else:
                raise SemanticError(f"Operador desconhecido: {node.operator}")
        elif isinstance(node, UnaryOp):
            operand_type = self.analyze(node.operand)
            if node.operator == "MINUS":
                if operand_type != "INT":
                    raise SemanticError("Operador '-' só pode ser aplicado a INT.")
                return "INT"
            elif node.operator == "NOT":
                if operand_type != "BOOL":
                    raise SemanticError("Operador 'NOT' só pode ser aplicado a BOOL.")
                return "BOOL"
            else:
                raise SemanticError(f"Operador unário desconhecido: {node.operator}")
        elif isinstance(node, Literal):
            if isinstance(node.value, bool):
                return "BOOL"
            elif isinstance(node.value, int):
                return "INT"
        elif isinstance(node, Identifier):
            return self.lookup_variable(node.name)
        elif isinstance(node, FuncCall):
            func_info = self.lookup_function(node.name)
            params = func_info["params"]
            if len(params) != len(node.args):
                raise SemanticError(
                    f"Chamada de função '{node.name}' com número inválido de argumentos. "
                    f"Esperado {len(params)}, recebido {len(node.args)}."
                )
            # Desempacotando (nome, tipo, linha) para cada parâmetro
            for ((param_name, param_type, param_line), arg) in zip(params, node.args):
                arg_type = self.analyze(arg)
                if arg_type != param_type:
                    raise SemanticError(
                        f"Type mismatch no argumento '{param_name}' da função '{node.name}'. "
                        f"Esperado '{param_type}', recebido '{arg_type}'."
                    )
            return func_info.get("return_type", "Unit")
        elif isinstance(node, BreakStatement):
            return "Unit"
        elif isinstance(node, ContinueStatement):
            return "Unit"
        else:
            raise SemanticError("Nó desconhecido na AST.")

    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        self.scope_stack.pop()

    def current_scope(self):
        return self.scope_stack[-1]

    def declare_variable(self, node: VarDecl):
        if node.name in self.current_scope():
            raise SemanticError(f"Variável '{node.name}' já declarada neste escopo.")
        self.current_scope()[node.name] = {"type": node.var_type, "is_const": node.is_const}

    def declare_function(self, node: FuncDecl):
        if node.name in self.current_scope():
            raise SemanticError(f"Função '{node.name}' já declarada neste escopo.")
        self.current_scope()[node.name] = {
            "params": node.params,
            "return_type": node.return_type
        }

    def lookup_variable(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope and isinstance(scope[name], dict) and "type" in scope[name]:
                return scope[name]["type"]
        raise SemanticError(f"Variável '{name}' não declarada.")

    def lookup_function(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope and isinstance(scope[name], dict) and "params" in scope[name]:
                return scope[name]
        raise SemanticError(f"Função '{name}' não declarada.")
