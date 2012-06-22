class SourceWalker:
    """
    Source code walker used to stumbler over interesting statements with compiler.walk()
    Some of the code is borrow from Zope
    """
    def __init__(self):
        self.imports = []
        self.functions = []

    def visitFunction(self, statement):
        """
        Collect function definitions
        """
        stmt = statement.asList()

        if not stmt[1].startswith("__"):
            self.functions.append(str(stmt[1]) + "(" + ",".join(stmt[2]) + ")")

    def visitFrom(self, statement):
        """
        Collect from imports
        """
        stmt = statement.asList()
        if stmt[0] == '__future__':
            # we don't care what's imported from the future
            return

        for orig_name, as_name in stmt[1]:
            # we don't care about from import *
            if orig_name == '*':
                continue

            self.imports.append(stmt[0] + "." + orig_name)

    def visitImport(self, statement):
        """
        Collect imports
        """
        for orig_name, as_name in statement.names:
            self.imports.append(orig_name)
