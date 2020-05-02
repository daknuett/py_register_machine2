#!/usr/bin/python3

from py_register_machine2.engine_tools.conversions import to_int

"""

**py_register_machine2.tools.assembler.directives**: Directives (Pseudoops) for the assembler

Directives for the assembler.
"""

class BaseDirective(object):
	"""
	Every Directive has to provide the following Attributes/Methods:

	* ``name`` (like ``.set``)
	* ``get_words(line)``: return the data to store
	* ``get_word_count(line)``: return the number of words to store
	* ``isstatic()`` returns True, if the reference should be static
	"""

	def __init__(self, name):
		self.name = name
	def get_words(self, line):
		return [int(line[0])]
	def get_word_count(self, line):
		return 1
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
	def get_word_count(self, line):
		return len(self.function(line))

class Zeros(BaseDirective):
	"""
	Usage: 
	::

		.zeros name n	

	Fills the next n words with zeros.
	"""
	def __init__(self, name = ".zeros"):
		self.name = name
	def get_words(self, line):
		return [0] * to_int(line[0])
	def get_word_count(self, line):
		return to_int(line[0])
	
class Padding(BaseDirective):
	"""
	Usage:
	::

		.padd name n v

	Fills the next n words with v.
	"""
	def __init__(self, name = ".padd"):
		self.name = name
	def get_words(self, line):
		number, value = line
		return [to_int(value)] * to_int(number)
	def get_word_count(self, line):
		return to_int(line[0])
	
