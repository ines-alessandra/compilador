class VarDeclNode:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class FuncDeclNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class IdentifierNode:
    def __init__(self, name):
        self.name = name

class IntegerNode:
    def __init__(self, value):
        self.value = value
