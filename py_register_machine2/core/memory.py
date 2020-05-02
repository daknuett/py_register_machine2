#!/usr/bin/python3


from ..core import parts


class BUS(parts.BUS):
	"""
	The processor's memory BUS, its devices are ROM and RAM.
	"""
	def __init__(self, width = 64, debug = 0):
		parts.BUS.__init__(self, width = width, debug = debug)
	
class ROM(parts.WordDevice):
	"""
	.. _ROM:

	**The Read Only Memory Device** 

	of the register machine stores either the boot code (for big programs) or
	the complete program, if the program is really small.

	The ROM is attached to the same BUS as the RAM and **always** includes the
	``offset 0``. The Program Counter (*PC*) of the Processor points to this word on powerup.

	Because RAM and ROM are in the same address space the following formula defines the size of
	RAM and ROM::

		addr_space = 2 ** memorybus.width
		ram.size + rom.size < addr_space

	A ``write`` call will raise ReadOnlyError_.
	
	"""
	def __init__(self, size, width = 64, debug = 0):
		parts.WordDevice.__init__(self, size, width = width, mode = 0b01, debug = debug)

	def program_word(self, offset, word):
		"""
		.. _program_word:

		Write the word ``word`` to the memory at offset ``offset``.
		Used to write the boot code.

		Might raise AddressError_, if the  offset exceeds the address space.

		"""
		if(offset >= self.size):
			raise AddressError("Offset({}) not in address space({})".format(offset, self.size))
		self.repr_[offset].setvalue(word)
	def program(self, prog, offset = 0):
		"""
		.. _program:

		Write the content of the iterable ``prog`` starting with the optional offset ``offset``
		to the device.

		Invokes program_word_.
		"""
		for addr, word in enumerate(prog):
			self.program_word(offset + addr, word)
		

class RAM(parts.WordDevice):
	"""
	.. _RAM:

	**The Random Access Memory Device**

	By default the RAM device is filled with zeros. 
	After poweron the Bootcode in the ROM might perform read/write operations on the RAM.
	If the register machine is to execute programs from the Flash device, this code
	has to be copied into the RAM.
	"""
	def __init__(self, size, width = 64, debug = 0):
		parts.WordDevice.__init__(self, size, width = width, mode = 0b11, debug = debug)

