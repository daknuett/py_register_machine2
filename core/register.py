#!/usr/bin/python3

"""
**py_register_machine2.core.register**: Registers for the register machine
"""

from ..core import parts
from ..engine_tools.conversions import int_to_bytes, bytes_to_int

class Register(parts.Register):
	"""
	The basic standard register. 
	Permitts read and write, does not execute any callbacks on read/write.

	See also: Register_
	"""
	def __init__(self, name, width = 64):
		parts.Register.__init__(self, name, width = width)

			
class OutputRegister(parts.Register):
	"""
	.. _OutputRegister:

	Used to print data to the user.
	The ``write`` call will convert ``word`` using ``chr`` and write
	the resulting ``str`` to ``open_stream``.

	The ``read`` call will return the last written ``word``.

	``open_stream`` might be a ``file`` (like ``sys.stdout``) or an ``io.StringIO`` object. 

	
	"""
	def __init__(self, name, open_stream, width = 64):
		parts.Register.__init__(self, name, width = width)
		self.open_stream = open_stream

	def write(self, word):
		"""
		.. _SOwrite:

		Write the ``chr`` representation of ``word`` to the ``open_stream``.
		
		If ``chr(word)`` fails due ``OverflowError``, a ``"?"`` will be written. 
		"""
		self.repr_.setvalue(word)
		try:
			self.open_stream.write(chr(self.repr_.getvalue()))
		except OverflowError:
			self.open_stream.write("?")

class StreamIORegister(parts.Register):
	"""
	.. _StreamIORegister:

	Input/Output Register via streams.

	The ``open_stream_in`` has to be readable, ``open_stream_out`` writeable.

	"""
	def __init__(self, name, open_stream_in, open_stream_out, width = 64):
		parts.Registers.__init(self, name, width = width)
		self.open_stream_in = open_stream_in
		self.open_stream_out = open_stream_out

	def read(self):
		"""
		Read a ``str`` from ``open_stream_in`` and convert it to an integer
		using ``ord``. The result will be truncated according to Integer_.
		"""
		self.repr_.setvalue(ord(self.open_stream_in.read(1)))
		return self.value.getvalue()
	def write(self, word):
		"""
		Works like SOwrite_.
		"""
		self.repr_.setvalue(word)
		try:
			self.open_stream.write(chr(self.value.getvalue()))
		except OverflowError:
			self.open_stream.write("?")

class BStreamIORegister(parts.Register):
	"""
	.. _BStreamIORegister:

	Works like StreamIORegister_, but ``open_stream_in`` and ``open_stream_out`` 
	are byte streams (like ``open("fname", "rb")``).
	
	* A ``read`` operation will read ``width // 8`` bytes and convert them to one ``int``.
	* A ``write`` operation will write ``width // 8`` bytes

	"""
	def __init__(self, name, open_stream_in, open_stream_out, width = 64):
		parts.Registers.__init(self, name, width = width)
		self.open_stream_in = open_stream_in
		self.open_stream_out = open_stream_out
	
	def read(self):
		"""
		Reads enough bytes from ``open_stream_in`` to fill the ``width`` 
		(if available) and converts them to an ``int``. Returns this ``int``.
		"""
		int_ = bytes_to_int(self.open_stream_in.read(math.ceil(self.width / 8)), self.width)
		self.repr_.setvalue(int_)
		return self.value.getvalue()

	def write(self, word):
		"""
		Converts the ``int`` ``word`` to a ``bytes`` object and writes them to
		``open_stream_out``.

		See ``int_to_bytes``.
		"""
		bytes_ = int_to_bytes(word, self.width)
		self.open_stream_out.write(bytes_)
	
