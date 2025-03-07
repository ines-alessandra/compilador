from parser import Program, VarDecl, FuncDecl, Block, Assignment, IfStatement, WhileStatement, ReturnStatement, BreakStatement, ContinueStatement, PrintStatement, Identifier, Literal, BinaryOp, UnaryOp, FuncCall

class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def generate(self, node):
        self.visit(node)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_Program(self, node: Program):
        print("Iniciando geração de código intermediário...\n")
        for declaration in node.declarations:
            self.visit(declaration)

    # Exemplo básico de geração intermediária
    def visit_VarDecl(self, node: VarDecl):
        initializer = self.visit(node.initializer)
        print(f"{node.name} = {initializer}")

    def visit_Assignment(self, node: Assignment):
        value = self.visit(node.value)
        print(f"{node.name} = {value}")

    def visit_Literal(self, node: Literal):
        return str(node.value)


    def visit_Identifier(self, node: Identifier):
        return node.name

    def visit_BinaryOp(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        print(f"{temp} = {left} {node.operator} {right}")
        return temp

    def visit_UnaryOp(self, node: UnaryOp):
        operand = self.visit(node.operand)
        temp = self.new_temp()
        print(f"{temp} = {node.operator}{operand}")
        return temp

    def visit_PrintStatement(self, node: PrintStatement):
        value = self.visit(node.value)
        print(f"print {value}")

    def visit_Identifier(self, node: Identifier):
        return node.name

    def visit_FuncCall(self, node: FuncCall):
        args = [self.visit(arg) for arg in node.args]
        temp = self.new_temp()
        args_str = ', '.join(args)
        print(f"{temp} = call {node.name}({args_str})")
        return temp

    def visit_FuncDecl(self, node: FuncDecl):
        params_str = ', '.join([f"{name}: {type_}" for name, type_ in node.params])
        print(f"function {node.name}({params_str}) : {node.return_type}")
        self.visit(node.body)
        print(f"end function {node.name}")

    def visit_Block(self, node: Block):
        for decl in node.declarations:
            self.visit(decl)

    def visit_IfStatement(self, node: IfStatement):
        condition = self.visit(node.condition)
        print(f"if {condition} goto then_label")
        if node.else_branch:
            print(f"goto else_label")
        print("then_label:")
        self.visit(node.then_branch)
        if node.else_branch:
            print("else_label:")
            self.visit(node.else_branch)

    def visit_WhileStatement(self, node: WhileStatement):
        print("while_label:")
        condition = self.visit(node.condition)
        print(f"if not {condition} goto end_while_label")
        self.visit(node.body)
        print("goto while_label")
        print("end_while_label")

    def visit_ReturnStatement(self, node: ReturnStatement):
        value = self.visit(node.value)
        print(f"return {value}")

    def visit_BreakStatement(self, node: BreakStatement):
        print("break")

    def visit_ContinueStatement(self, node: ContinueStatement):
        print(f"continue")

    def visit_PrintStatement(self, node: PrintStatement):
        value = self.visit(node.value)
        print(f"print {value}")

    def visit_Identifier(self, node: Identifier):
        return node.name
