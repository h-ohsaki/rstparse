#!/usr/bin/env python3
#
#
# Copyright (c) 2019, Hiroyuki Ohsaki.
# All rights reserved.
#

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# https://docutils.readthedocs.io/en/sphinx-docs/ref/rst/restructuredtext.html
# https://docutils.readthedocs.io/en/sphinx-docs/ref/rst/directives.html

import re
import sys
import pydoc

DIRECTIVES_TO_INCLUDE = [
    'autosummary_', 'module', 'currentmodule', 'automodule', 'class',
    'autoclass', 'method', 'classmethod', 'coroutinemethod', 'automethod',
    'staticmethod', 'function', 'autofunction', 'c:function', 'data',
    'attribute', 'exception', 'c:var', 'c:type', 'decorator', 'envvar',
    'autodata'
]

class RSTParser:
    def __init__(self, file=None):
        self.lines = []
        self.indices = {}

    def read(self, stream):
        """Read all lines from stream STREAM, and store the lines in the
        object attribute LINES.  All `autosummary` directives are converted to
        pseudo `autosummary_` directives."""

        def repl_autoloaded(m):
            buf = m.group(1)
            buf = re.sub(r'^ +', '.. autosummary_:: ', buf, flags=re.MULTILINE)
            return '\n' + buf + '\n\n'

        buf = stream.read()
        buf = re.sub(r'\n.. autosummary::.*?\n\n(.+?)\n\n',
                     repl_autoloaded,
                     buf,
                     flags=re.DOTALL)
        self.lines = buf.splitlines()

    def parse_directive(self, astr):
        """Check the existence of an ReST directive in string ASTR.  Return a
        tuple of (DIRECTIVE, VALUE) if it exists.  If a directive is not
        found, retrun (None, None)."""
        m = re.search(r'\.\. *([^:]+):: *(.*)', astr)
        if m:
            return m.groups()
        else:
            return None, None

    def compose_name(self, *kargs):
        """Return a string joined by '.' from the list of arguments."""
        components = [n for n in kargs if n is not None]
        return '.'.join(components)

    def is_valid_name(self, name):
        """Check if name NAME is a valid Python symbol name.  Return True if
        valid and return False otherwise."""
        try:
            obj = pydoc.locate(name)
        except pydoc.ErrorDuringImport:
            return False
        if obj is not None:
            return True
        return False

    def resolve_name(self, name, module=None, cls=None):
        """Locate a valid symbol name NAME in either global name space, module
        MODULE, or class CLS.  Retun a valid symbol name as a string.  Return
        None if no valid symbol is found."""
        if module is None:
            module = self.module
        if cls is None:
            cls = self.cls
        for m in [module, None]:
            for c in [cls, None]:
                n = self.compose_name(m, c, name)
                if self.is_valid_name(n):
                    return n
        return None

    def pydoc_lines_for(self, name):
        """Return a list of lines for PyDoc document for NAME.  If no document
        for NAME is found, return an empty array."""
        name = self.resolve_name(name)
        if name is None:
            return []
        doc = pydoc.render_doc(name)
        lines = doc.splitlines()
        # discard the header lines
        return lines[2:]

    def reset_context(self):
        self.module = None
        self.cls = None

    def track_context(self, line):
        key, val = self.parse_directive(line)
        if key in ['module', 'currentmodule', 'automodule']:
            self.module = val
        if key in ['class', 'autoclass']:
            val = re.sub(r' *\(.+', '', val)
            self.cls = val
        # class description in PyDoc document
        m = re.search(r' = class (\w+)', line)
        if m:
            self.cls = m.group(1)
        line = re.sub(r'.\x08', '', line)
        # class description
        m = re.match(r' *class (\w+)', line)
        if m:
            self.cls = m.group(1)

    def expand_auto_directives(self):
        """Expand all auto directives with corresponding PyDoc documents."""
        lines = []
        self.reset_context()
        for line in self.lines:
            lines.append(line)
            self.track_context(line)
            key, val = self.parse_directive(line)
            if key and key.startswith('auto') and val:
                lines += self.pydoc_lines_for(val)
        self.lines = lines

    def register_index(self, name, lineno=None, module=None, cls=None):
        """Record the symbol name NAME with its line number LINENO in the
        object attribute INDICES.  Symbol name NAME is resolved before
        registration."""
        name = re.sub(r'\(.+', '', name)
        name = self.resolve_name(name, module=module, cls=cls)
        if name:
            self.indices[name] = lineno

    def parse_indices(self):
        """Parse all lines and build indices for module, class, attribute
        descriptions."""
        self.reset_context()
        for lineno, line in enumerate(self.lines):
            key, val = self.parse_directive(line)
            if key in DIRECTIVES_TO_INCLUDE and val:
                self.register_index(val, lineno)
            # parse methods
            m = re.search(r'\|  (\w\x08[\w\x08]+)', line)
            if m:
                name = re.sub(r'.\x08', '', m.group(1))
                name = self.cls + '.' + name
                self.register_index(name, lineno)
            self.track_context(line)

    def parse(self):
        self.expand_auto_directives()
        self.parse_indices()

def main():
    for file in sys.argv[1:]:
        rst = RSTParser()
        with open(file) as f:
            rst.read(f)
        rst.parse()
        for key, val in rst.indices.items():
            print(key, val)
        for n, line in enumerate(rst.lines):
            print('{:5} {}'.format(n, line))

if __name__ == "__main__":
    main()
