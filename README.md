# rstparse Package

rstparse - expand and analyze RST (reStructureText) documents with auto*-directives

# DESCRIPTION

This manual page documents **rstparse**, a Python module for parsing RST
(reStructureText) documents.  

Many documents of Python and its standard libraries, as well as a vast number
of third party modules are written as RST (reStructureText) markup documents.
RST documents are easier to handle since, similarly to other markup document
formats such as Markdown, it is mostly a plain text file with several
additional notations.

Since RST documents are plain text files, you can easily browse those
documents using your favorite tools like pagers (e.g., `more`, `less`, and
`lv`) and also you can search for topics that you are interested in using
common tools such as `grep`.

However, a significant portion of RST files use *auto* directives (e.g.,
autosummary, automodule, autoclass, and autofunction), which ask the RST
parser to include the contents from somewhere outside the RST document.  For
instance, if an RST file contains a line,

```
.. autosummary: good_func
```

the description of `good_func` is not contained in this file.  `autosummary`
means the description must be inserted here.  It is an RST parser's
responsibility to identify where the description of `good_func` is stored.
**rstparse** module parses an RST file and expands all auto*-directives.

# EXAMPLE

```python
import rstparse

file = 'foo.rst'
rst = rstparse.Parser()
with open(file) as f:
    rst.read(f)
rst.parse()
for line in rst.lines:
	print(line)
```

# INSTALLATION

```python
pip3 install rstparser
```

# AVAILABILITY

The latest version of **rstparser** module is available at PyPI
(https://pypi.org/project/rstparser/) .

# SEE ALSO

- reStructuredText Markup Specification

  https://docutils.readthedocs.io/en/sphinx-docs/ref/rst/restructuredtext.html

- reStructuredText Directives

  https://docutils.readthedocs.io/en/sphinx-docs/ref/rst/directives.html

# AUTHOR

Hiroyuki Ohsaki <ohsaki[atmark]lsnl.jp>
