# ast_utils.py
import json
from compiler.parser_orginal import (
    Program, VarDecl, FuncDecl, Block, Assignment,
    IfStatement, WhileStatement, ReturnStatement,
    BreakStatement, ContinueStatement, PrintStatement,
    BinaryOp, UnaryOp, Literal, Identifier, FuncCall
)

def ast_to_dict(node):
    """Converts an AST node to a serializable dictionary"""
    if isinstance(node, (int, float, str, bool)) or node is None:
        return node
    
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    
    if not hasattr(node, '__class__'):
        return str(node)
    
    node_dict = {
        "type": node.__class__.__name__,
    }
    
    # Add line number if available
    if hasattr(node, 'line') and node.line is not None:
        node_dict['line'] = node.line
    
    # Handle specific node types
    if isinstance(node, Program):
        node_dict['declarations'] = ast_to_dict(node.declarations)
    
    elif isinstance(node, VarDecl):
        node_dict.update({
            'is_const': node.is_const,
            'name': node.name,
            'var_type': node.var_type,
            'initializer': ast_to_dict(node.initializer)
        })
    
    elif isinstance(node, FuncDecl):
        node_dict.update({
            'name': node.name,
            'params': [{'name': p[0], 'type': p[1], 'line': p[2]} for p in node.params],
            'return_type': node.return_type,
            'body': ast_to_dict(node.body)
        })
    
    elif isinstance(node, Block):
        node_dict['declarations'] = ast_to_dict(node.declarations)
    
    elif isinstance(node, Assignment):
        node_dict.update({
            'name': node.name,
            'value': ast_to_dict(node.value)
        })
    
    elif isinstance(node, IfStatement):
        node_dict.update({
            'condition': ast_to_dict(node.condition),
            'then_branch': ast_to_dict(node.then_branch),
            'else_branch': ast_to_dict(node.else_branch) if node.else_branch else None
        })
    
    elif isinstance(node, WhileStatement):
        node_dict.update({
            'condition': ast_to_dict(node.condition),
            'body': ast_to_dict(node.body)
        })
    
    elif isinstance(node, ReturnStatement):
        node_dict['value'] = ast_to_dict(node.value)
    
    elif isinstance(node, (BreakStatement, ContinueStatement)):
        pass  # No additional fields
    
    elif isinstance(node, PrintStatement):
        node_dict['value'] = ast_to_dict(node.value)
    
    elif isinstance(node, BinaryOp):
        node_dict.update({
            'left': ast_to_dict(node.left),
            'operator': node.operator,
            'right': ast_to_dict(node.right)
        })
    
    elif isinstance(node, UnaryOp):
        node_dict.update({
            'operator': node.operator,
            'operand': ast_to_dict(node.operand)
        })
    
    elif isinstance(node, Literal):
        node_dict['value'] = node.value
    
    elif isinstance(node, Identifier):
        node_dict['name'] = node.name
    
    elif isinstance(node, FuncCall):
        node_dict.update({
            'name': node.name,
            'args': ast_to_dict(node.args)
        })
    
    else:
        raise ValueError(f"Unknown AST node type: {node.__class__.__name__}")
    
    return node_dict

def save_ast_to_file(ast, filename):
    """
    Saves the AST to a JSON file
    Args:
        ast: The root node of the AST (usually Program)
        filename: Output file path
    """
    ast_dict = ast_to_dict(ast)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ast_dict, f, indent=2, ensure_ascii=False)

def print_ast(ast):
    """Prints the AST in a readable JSON format"""
    ast_dict = ast_to_dict(ast)
    print(json.dumps(ast_dict, indent=2, ensure_ascii=False))