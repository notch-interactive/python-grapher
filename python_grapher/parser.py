import ast

class SourceWalker(ast.NodeVisitor):
    """
    Source code walker used to stumbler over interesting statements with compiler.walk()
    Some of the code is borrow from Zope
    """
    def __init__(self):
        self.imports = []
        self.functions = []

    def visit_FunctionDef(self, statement):
        """
        Collect function definitions
        """
        # if stmt[1] == "__init__":
        #     import pudb; pudb.set_trace()

        if not statement.name.startswith("__"):
            func_str = str(statement.name) + "("

            for arg in statement.args.args:
                func_str += str(arg.id) + ", "

            func_str = func_str[:-2]
            func_str += ")"
            self.functions.append(func_str)


    def visit_ImportFrom(self, statement):
        """
        Collect from imports
        """
        for imp in statement.names:
            self.imports.append(statement.module + "." + imp.name)


    def visit_Import(self, statement):
        """
        Collect imports
        """
        for node in statement.names:
            self.imports.append(node.name)
