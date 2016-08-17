#!/usr/bin/python3

"""
Directives for the assembler.
"""

class BaseDirective(object):
	"""
	Every Directive has to provide the following Attributes/Methods:

	* ``name`` (like ``.set``)
	* ``get_words(line)``: return the data to store
	* ``isstatic()`` returns True, if the reference should be static
	"""

	def __init__(self, name):
		self.name = name
	def get_words(self, line):
		return [int(line[0])]
	def isstatic(self):
		return False


class ConvertingDirective(BaseDirective):
	"""
	The function ``function`` will have to take the rest of the line (as a list)
	and convert it to an iterable of ``int`` objects

	**Example**: The ``.string`` directive::

		# usage: .string name string
		# ie.: .string foo this is a test

		def string_function(line):
			line = " ".join(line)
			res = []
			for char in line:
				res.append(ord(char))
			return res
	"""
	def __init__(self, name, function):
		BaseDirective.__init__(self, name)
		self.function = function

	def get_words(self, line):
		return self.function(line)
