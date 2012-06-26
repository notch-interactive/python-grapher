import sys
import inspect
import ast
from python_grapher.parser import SourceWalker


class Generator(object):
    """
    Generate DOT code for Python classes
    Some of the code is borrowed from django_extensions
    """
    def __init__(self, font_size=9, color_background="white", color_properties="", color_class=""):
        self.known_classes = []
        self.known_modules = []
        self.font_size = font_size
        self.color_background = color_background
        self.color_properties = color_properties
        self.color_class = color_class


    def write_node_start(self, node_name):
        """
        Return DOT code for start of new node element
        """
        return "\n" + """"%s" [shape="box", label=<\n<TABLE BGCOLOR="%s" BORDER="0" CELLBORDER="0" CELLSPACING="0">
         <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="%s"><FONT FACE="Helvetica Bold" COLOR="white">%s</FONT></TD></TR>""" % (node_name, self.color_properties, self.color_class, node_name)


    def write_node_end(self):
        """
        Return DOT code for end of node element
        """
        return "</TABLE>\n>];\n\n"


    def write_property(self, prop):
        """
        Return DOT code for a property
        """
        return "<TR><TD ALIGN=\"LEFT\" BORDER=\"0\">%s</TD></TR>" % (prop,)


    def write_graph_start(self):
        """
        Return DOT code for the start of a new graph
        """
        return """
digraph name {
  fontname = "Helvetica"
  fontsize = %d

  node [
    fontname = "Helvetica"
    fontsize = %d
    shape = "plaintext"
    color = "%s"
  ]
  edge [
    fontname = "Helvetica"
    fontsize = %d
  ]

""" % (self.font_size, self.font_size, self.color_background, self.font_size)


    def write_graph_end(self):
        """
        Return DOT code for end of graph
        """
        return """
}
"""

    def get_full_classname(self, cls):
        """
        Return full qualified name of given class
        """
        name = cls.__module__

        if cls.__name__ != "type":
            name += "." + cls.__name__

        return name


    def write_module(self, module, with_properties):
        """
        Return DOT code for given module
        Include function with_properties is True
        """
        if inspect.isclass(module):
            return self.write_class(module, with_properties)

        if not inspect.ismodule(module):
            return ""

        modulename = module.__name__
        content = ""

        # Module already drawn?
        if modulename in self.known_modules:
            return content

        # Draw class
        self.known_modules.append(modulename)
        content += self.write_node_start(modulename)

        # Parse source file
        if hasattr(module, "__file__"):
            module_file = module.__file__.replace(".pyc", ".py")
        else:
            module_file = ""

        if module_file.endswith(".py"):
            nodes = ast.parse(open(module_file).read())
            log = SourceWalker()
            log.visit(nodes)

            if with_properties:
                for prop in log.functions:
                    content += self.write_property(prop)

            content += self.write_node_end()

            # Imports
            mod_path = modulename.split(".")

            for mod in log.imports:
                # display only imports from same base package
                if mod.startswith(mod_path[0]) and mod not in self.known_modules:
                    tmp = mod.split(".")
                    imp_class_name = tmp.pop(-1)
                    imp_package_name = ".".join(tmp)

                    try:
                        if imp_package_name:
                            __import__(imp_package_name)
                            imp_module = getattr(sys.modules[imp_package_name], imp_class_name)
                        else:
                            __import__(imp_class_name)
                            imp_module = sys.modules[imp_class_name]

                        content += self.write_class(imp_module, with_properties)
                        content += "\"%s\" -> \"%s\" [style=solid arrowhead=normal arrowtail=normal label=\"Uses\"];\n" % (modulename, mod)
                    except ImportError:
                        pass
        else:
            content += self.write_node_end()

        return content



    def write_class(self, cls, with_properties):
        """
        Return DOT code for given class
        Include class properties if with_properties is True
        """
        if inspect.ismodule(cls):
            return self.write_module(cls, with_properties)

        if not inspect.isclass(cls):
            return ""

        content = ""
        classname = self.get_full_classname(cls)

        # Class already drawn?
        if classname in self.known_classes:
            return content

        # First draw base classes
        for base_class in cls.__bases__:
            cls_path = classname.split(".")

            if cls_path[0] in self.get_full_classname(base_class) and base_class != object:
                content += self.write_class(base_class, with_properties)


        # Draw class
        self.known_classes.append(classname)
        content += self.write_node_start(classname)

        # Parse source file
        module_file = sys.modules[cls.__module__].__file__.replace(".pyc", ".py")

        if module_file.endswith(".py"):
            nodes = ast.parse(open(module_file).read())
            log = SourceWalker()
            log.visit(nodes)

            if with_properties:
                for prop in log.functions:
                    content += self.write_property(prop)

            content += self.write_node_end()


            # Draw edges between parent and child classes
            for base_class in cls.__bases__:
                if base_class != object:
                    content += "\"%s\" -> \"%s\" [style=dotted arrowhead=normal arrowtail=normal];\n" % (classname, self.get_full_classname(base_class))


            # Imports
            mod_path = cls.__module__.split(".")

            for mod in log.imports:
                # display only imports from same base package
                if mod not in self.known_classes:
                    tmp = mod.split(".")
                    imp_class_name = tmp.pop(-1)
                    imp_package_name = ".".join(tmp)

                    try:
                        if imp_package_name:
                            __import__(imp_package_name)
                            imp_module = getattr(sys.modules[imp_package_name], imp_class_name)
                        else:
                            __import__(mod)
                            imp_module = sys.modules[mod]

                        content += self.write_class(imp_module, with_properties)
                        content += "\"%s\" -> \"%s\" [style=solid arrowhead=normal arrowtail=normal label=\"Uses\"];\n" % (classname, mod)
                    except ImportError:
                        pass
        else:
            content += self.write_node_end()

        return content
