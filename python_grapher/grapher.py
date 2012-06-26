import sys
import tempfile
import pygraphviz as pgv
from python_grapher.dot import Generator

class Grapher(object):
    """
    Generate a graph of Python classes
    """
    def __init__(self, font_size=9, color_background="white", color_properties="", color_class=""):
        self.generator = Generator(font_size, color_background, color_properties, color_class)
        self.template = ""


    def draw_modules(self, module_list, **kwargs):
        """
        Generate diagram of a given list of Python modules
        Include module functions if with_properties is True
        """
        self.template = self.generator.write_graph_start()

        for module in module_list:
            __import__(module)
            self.template += self.generator.write_module(sys.modules[module], **kwargs)

        self.template += self.generator.write_graph_end()


    def draw_classes(self, class_list, **kwargs):
        """
        Generate diagramm of a given list of classes
        Include class properties if with_properties is True
        """
        self.template = self.generator.write_graph_start()

        for cls in class_list:
            cls_path = cls.split(".")
            cls_name = cls_path.pop(-1)

            if cls_path:
                __import__(".".join(cls_path))
                self.template += self.generator.write_class(getattr(sys.modules[".".join(cls_path)], cls_name), **kwargs)
            else:
                __import__(cls_name)
                self.template += self.generator.write_class(cls_name, **kwargs)

        self.template += self.generator.write_graph_end()


    def write_to_file(self, output_file="graph.png", layout_manager="fdp", debug=False):
        """
        Write diagram to file
        Optionally you can specify the filename and the Graphviz layout manager to used
        """
        if debug:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            print "Generating DOT file " + tmpfile.name
        else:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)

        tmpfile.write(self.template)
        tmpfile.seek(0)

        # draw graph from dot file
        vizdata = tmpfile.name
        graph = pgv.AGraph(vizdata)

        graph.layout(prog=layout_manager)
        graph.draw(output_file)
