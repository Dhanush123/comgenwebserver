import sys
import ast
import io
import os
import csv

from comgenwebserver.constants import FUNCTION_NAME_COLUMN, AST_COLUMN, AST_CSV_FIELDNAMES


class ASTFunctionsExtractor(ast.NodeVisitor):

    def __init__(self, python_file_path, ast_file_path):
        self.ast_file_path = ast_file_path
        # if isinstance(str, python_file_path):
        #     self.ast_object = ast.parse(open(python_file_path).read())
        # else:
        python_file_path.seek(0)
        self.ast_object = ast.parse(python_file_path.read())
        # print('python_file_path', python_file_path.read())
        self.single_function_ast_str = ''
        self.single_function_name = ''

        self.csv_writer = csv.DictWriter(
            self.ast_file_path, fieldnames=AST_CSV_FIELDNAMES)
        self.csv_writer.writeheader()
        self.ast_file_path.seek(0)

        # with open(self.ast_file_path, 'a+') as ast_file:
        # csv_writer = csv.writer(ast_file_path, delimiter=',')
        # csv_writer.writerow([FUNCTION_NAME_COLUMN, AST_COLUMN])
        # ast_file_path.seek(0)

    def visit_FunctionDef(self, node):
        try:
            # only want docstrings that are in ascii so I can read + simplifies project
            temp_docstring = ast.get_docstring(node)
            if temp_docstring:
                temp_docstring = temp_docstring.encode(
                    'ascii').decode('utf-8')
            # print('temp_docstring', temp_docstring)
            if not temp_docstring:
                self.node_visit(node)
                self.single_function_ast_str = self.single_function_ast_str.encode(
                    'ascii').decode('utf-8')
                if self.single_function_ast_str:
                    self.save_data()
                    print("saving data...")
            print("clearing...")
            self.single_function_ast_str = ''
            self.single_function_name = ''
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass

    def args_to_str(self, args):
        return f'args{len(args)}'

    def assign_to_str(self, node):
        return type(node.value).__name__

    def expr_to_str(self, node):
        return node.value.__class__.__name__

    def constant_to_str(self, node):
        return f'{type(node.value).__name__}'

    def node_to_str(self, node):
        ast_set = ("Delete", "For", "AsyncFor",
                   "While", "If", "With", "AsyncWith", "Raise",
                   "Try", "Assert", "Global", "Nonlocal", "Pass",
                   "Break", "Continue", "ExceptHandler",
                   "BoolOp", "NamedExpr", "BinOp", "UnaryOp", "Lambda",
                   "IfExp", "Dict", "Set", "ListComp", "SetComp", "DictComp",
                   "GeneratorExp", "Await", "Compare", "FormattedValue", "JoinedStr"
                   "Constant", "Attribute", "Subscript", "Starred", "Name"
                   "List", "Tuple")
        if isinstance(node, ast.AST):
            fields_list = []
            if node.__class__.__name__ == "FunctionDef":
                self.single_function_name = node.name  # actual name of the function
                fields_list.append(node.__class__.__name__)
                if node.args.args:
                    fields_list.append(self.args_to_str(node.args.args))
            elif node.__class__.__name__ in ("Assign", "AugAssign"):
                fields_list.append("Assign")
            elif node.__class__.__name__ in ("Yield", "YieldFrom"):
                fields_list.append("Yield")
            elif node.__class__.__name__ == "Expr":
                fields_list.append(self.expr_to_str(node))
            elif node.__class__.__name__ == "Constant":
                fields_list.append(self.constant_to_str(node))
            elif node.__class__.__name__ == "Call":
                fields_list.append(self.args_to_str(node.args))
            else:
                fields_list.append(node.__class__.__name__)
            return f"{' '.join(fields_list)}" if fields_list else ""
        else:
            return repr(node)

    def node_visit(self, node):
        node_str = self.node_to_str(node).strip()
        if node_str:
            self.single_function_ast_str += node_str + " "
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for value_item in value:
                    if isinstance(value_item, ast.AST):
                        self.node_visit(value_item)
            elif isinstance(value, ast.AST):
                self.node_visit(value)

    def save_data(self):
        # with open(self.ast_file_path, 'a+') as ast_file:
        self.csv_writer.writerow({FUNCTION_NAME_COLUMN: self.single_function_name,
                                  AST_COLUMN: self.single_function_ast_str})
        self.ast_file_path.seek(0)
        # print('data writing!!!', self.single_function_name,
        #       self.single_function_ast_str)
