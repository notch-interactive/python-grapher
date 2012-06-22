Python-Grapher
==============

Generate diagrams from your Python classes.


Requirements
------------

* Pygraphviz


Usage
-----

.. code-block:: Python

  from python_grapher import Grapher
  graph = Grapher()
  graph.draw_classes(["django.http.HttpResponse"])
  graph.write_to_file("mygraph.png", "dot")
