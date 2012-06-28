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
        self.drawn_objects = []
        self.drawn_edges = {}
        self.font_size = font_size
        self.color_background = color_background
        self.color_properties = color_properties
        self.color_class = color_class
        self.import_depth = 0


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


    def write_module(self, module, **kwargs):
        """
        Return DOT code for given module
        Include function with_properties is True
        """
        if inspect.isclass(module):
            return self.write_class(module, **kwargs)

        if not inspect.ismodule(module):
            return ""

        modulename = module.__name__
        content = ""

        # Module already drawn?
        if modulename in self.drawn_objects:
            return content

        # Draw class
        self.drawn_objects.append(modulename)
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

            if kwargs.get("with_properties", False):
                for prop in log.functions:
                    content += self.write_property(prop)

            content += self.write_node_end()

            # Imports
            if self.import_depth < kwargs.get("depth", 1):
                self.import_depth += 1

                for mod in log.imports:
                    tmp = mod.split(".")
                    imp_class_name = tmp.pop(-1)
                    imp_package_name = ".".join(tmp)

                    try:
                        if imp_package_name:
                            base_package = tmp[0]
                            __import__(imp_package_name)

                            if imp_class_name != "*":
                                imp_module = getattr(sys.modules[imp_package_name], imp_class_name)

                                if inspect.isfunction(imp_module):
                                    imp_module = sys.modules[imp_package_name]
                                    mod = imp_module.__name__
                            else:
                                imp_module = sys.modules[imp_package_name]
                                mod = imp_module.__name__

                        else:
                            base_package = imp_class_name
                            __import__(imp_class_name)
                            imp_module = sys.modules[imp_class_name]

                        # already drawn?
                        if not mod or mod in self.drawn_objects:
                            continue

                        # display only imports from same base package
                        if not kwargs.get("package_boundaries", False) or base_package in modulename:
                            content += self.write_class(imp_module, **kwargs)
                            self.drawn_objects.append(mod)

                            if mod not in self.drawn_edges.get(modulename, []):
                                content += "\"%s\" -> \"%s\" [style=solid arrowhead=normal arrowtail=normal label=\"Uses\"];\n" % (modulename, mod)
                                self.drawn_edges.setdefault(modulename, []).append(mod)
                    except ImportError:
                        pass
        else:
            content += self.write_node_end()

        return content



    def write_class(self, cls, **kwargs):
        """
        Return DOT code for given class
        Include class properties if with_properties is True
        """
        if inspect.ismodule(cls):
            return self.write_module(cls, **kwargs)

        if not inspect.isclass(cls):
            return ""

        content = ""
        classname = self.get_full_classname(cls)

        # Class already drawn?
        if classname in self.drawn_objects:
            return content

        # First draw base classes
        for base_class in cls.__bases__:
            cls_path = classname.split(".")

            if cls_path[0] in self.get_full_classname(base_class) and base_class != object:
                content += self.write_class(base_class, **kwargs)


        # Reset depth counter otherwise only imports from base classes are drawn
        if self.import_depth == kwargs.get("depth", 1):
            self.import_depth -= 1

        # Draw class
        self.drawn_objects.append(classname)
        content += self.write_node_start(classname)

        # Parse source file
        if hasattr(sys.modules[cls.__module__], "__file__"):
            module_file = sys.modules[cls.__module__].__file__.replace(".pyc", ".py")
        else:
            module_file = ""

        if module_file.endswith(".py"):
            nodes = ast.parse(open(module_file).read())
            log = SourceWalker()
            log.visit(nodes)

            if kwargs.get("with_properties", False):
                for prop in log.functions:
                    content += self.write_property(prop)

            content += self.write_node_end()


            # Draw edges between parent and child classes
            for base_class in cls.__bases__:
                if base_class != object and self.get_full_classname(base_class) not in self.drawn_edges.get(classname, []):
                    content += "\"%s\" -> \"%s\" [style=dotted arrowhead=normal arrowtail=normal];\n" % (classname, self.get_full_classname(base_class))
                    self.drawn_edges.setdefault(classname, []).append(self.get_full_classname(base_class))

            # Imports
            if self.import_depth < kwargs.get("depth", 1):
                self.import_depth += 1

                for mod in log.imports:
                    tmp = mod.split(".")
                    imp_class_name = tmp.pop(-1)
                    imp_package_name = ".".join(tmp)

                    try:
                        if imp_package_name:
                            base_package = tmp[0]
                            __import__(imp_package_name)

                            if imp_class_name != "*":
                                imp_module = getattr(sys.modules[imp_package_name], imp_class_name)

                                if inspect.isfunction(imp_module):
                                    imp_module = sys.modules[imp_package_name]
                                    mod = imp_module.__name__
                            else:
                                imp_module = sys.modules[imp_package_name]
                                mod = imp_module.__name__
                        else:
                            base_package = mod
                            __import__(mod)
                            imp_module = sys.modules[mod]

                        # already drawn?
                        if not mod or mod in self.drawn_objects:
                            continue

                        # display only imports from same base package
                        if not kwargs.get("package_boundaries", False) or base_package in classname:
                            content += self.write_class(imp_module, **kwargs)
                            self.drawn_objects.append(mod)

                            if mod not in self.drawn_edges.get(classname, []):
                                content += "\"%s\" -> \"%s\" [style=solid arrowhead=normal arrowtail=normal label=\"Uses\"];\n" % (classname, mod)
                                self.drawn_edges.setdefault(classname, []).append(mod)
                    except ImportError:
                            pass
        else:
            content += self.write_node_end()

        return content
