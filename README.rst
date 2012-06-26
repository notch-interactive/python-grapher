Python-Grapher
==============

Generate diagrams from your Python classes and modules.


Requirements
------------

* Pygraphviz


Usage
-----

.. code-block:: Python

  from python_grapher import Grapher
  graph = Grapher()
  graph.draw_classes(["django.http.HttpResponse"])
  print graph.template # the DOT code
  graph.write_to_file("mygraph.png", "dot")
