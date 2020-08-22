import ast


class DocstringInserter(ast.NodeTransformer):
    ast_map = {}

    def __init__(self, ast_map):
        self.ast_map = ast_map

    def visit_FunctionDef(self, node):
        if node.__class__.__name__ == 'FunctionDef' and node.name in self.ast_map:
            docstring = self.ast_map[node.name]['docstring']
            new_docstring_node = make_docstring_node(docstring)
            # Assumes the existing docstring is the first node
            # in the function body.
            node.body[0] = new_docstring_node
        else:
            node.body.insert(0, new_docstring_node)
        return node


def make_docstring_node(docstring):
    return ast.Expr(value=ast.Str(docstring))
