from distutils.command.build_py import build_py as _build_py
from distutils.core import setup

class build_py(_build_py):
    CLASSIFIERS = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]

    setup(name="python_grapher",
          version="0.1.0",
          author="Notch Interactive GmbH",
          author_email="info@notch-interactive.com",
          url="http://github.com/notch-interactive/python-grapher",
          description="Draw diagrams from your Python classes",
          packages=["python_grapher"],
    )
