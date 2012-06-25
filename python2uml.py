#!/usr/bin/python

#
# Python tool to automatically draw UML diagramms from Python classes
# -------------------------------------------------------------------
#
# Author:
# Bastian Ballmann <bastian.ballmann@notch-interactive.com>
# Notch Interactive GmbH <http://www.notch-interactive.com>
#
# License: BSD
#

import argparse
from python_grapher import Grapher

parser = argparse.ArgumentParser()
parser.add_argument("-cb", "--color-background", default="white", help="Color of graph background")
parser.add_argument("-cc", "--color-class", default="olivedrab4", help="Color of classname background")
parser.add_argument("-cp", "--color-properties", default="palegoldenrod", help="Color of property background")
parser.add_argument("-d", "--debug", action="store_true", help="Run in debug mode")
parser.add_argument("-fs", "--font-size", default="9", type=int, help="Font size")
parser.add_argument("-lm", "--layout-manager", default="fdp", help="Graphviz layout manager")
parser.add_argument("-o", "--output-file", default="graph.png", help="File the graph gets written to")
parser.add_argument("-p", "--with-properties", action="store_true", help="Draw class properties")
parser.add_argument("classes")
args = parser.parse_args()

graph = Grapher(args.font_size, args.color_background, args.color_properties, args.color_class)
graph.draw_classes(args.classes.split(","), args.with_properties)
graph.write_to_file(args.output_file, args.layout_manager)
print "Generated " + args.output_file
