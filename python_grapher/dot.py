import sys
import inspect
import compiler
from python_grapher.parser import SourceWalker


class Generator(object):
    def __init__(self, font_size=9, color_background="white", color_properties="", color_class=""):
        self.known_classes = []
        self.font_size = font_size
        self.color_background = color_background
        self.color_properties = color_properties
        self.color_class = color_class


    def pretty_class_name(self, cls):
        return "'" + str(cls).replace("<class '", "").replace("'>", "") + "'"


    def write_node_start(self, node_name):
        return "\n" + """"%s" [shape="box", label=<\n<TABLE BGCOLOR="%s" BORDER="0" CELLBORDER="0" CELLSPACING="0">
         <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="%s"><FONT FACE="Helvetica Bold" COLOR="white">%s</FONT></TD></TR>""" % (node_name, self.color_properties, self.color_class, node_name)


    def write_node_end(self):
        return "</TABLE>\n>];\n\n"


    def write_property(self, prop):
        return "<TR><TD ALIGN=\"LEFT\" BORDER=\"0\">%s</TD></TR>" % (prop,)


    def write_head(self):
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


    def write_tail(self):
        return """
}
"""

    def get_full_classname(self, obj):
        name = obj.__module__

        if obj.__name__ != "type":
            name += "." + obj.__name__

        return name


    def draw_class(self, cls, **kwself):
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
                content += self.draw_class(base_class, **kwself)


        # Draw class
        self.known_classes.append(classname)
        content += self.write_node_start(classname)

        # Parse source file
        module_file = sys.modules[cls.__module__].__file__.replace(".pyc", ".py")
        ast = compiler.parseFile(module_file)
        log = SourceWalker()
        compiler.walk(ast, log)

        if kwself.get("with_properties"):
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
            if mod.startswith(mod_path[0]) and mod not in self.known_classes:
                tmp = mod.split(".")
                imp_class_name = tmp.pop(-1)
                imp_package_name = ".".join(tmp)
                __import__(imp_package_name)
                imp_module = getattr(sys.modules[imp_package_name], imp_class_name)

                content += self.draw_class(imp_module, **kwself)
                content += "\"%s\" -> \"%s\" [style=solid arrowhead=normal arrowtail=normal label=\"Uses\"];\n" % (classname, mod)

        return content
