#!/usr/bin/python3

"""
**py_register_machine2.core.device**: Device BUS and attached devices
"""

from ..core import parts

class BUS(parts.BUS):
	"""
	The processor's device BUS, usually the Flash is attached to this BUS,
	but there might be more devices.
	"""
	def __init__(self, width = 64, debug = 0):
		parts.BUS.__init__(self, width = width, debug = debug)


class Flash(parts.WordDevice):
	"""
	.. _Flash:
	
	**The Program Flash**

	If the size of the program exceeds the size of the ROM the program has to be written into
	the Flash. The Flash is a Read/Write device and contains

	* The Program
	* Constants
	* Static Variables

	The Flash is a WordDevice and attached to the ``device.BUS`` .
	"""

	def __init__(self, size, width = 64, debug = 0):
		parts.WordDevice.__init__(self, size, width = width, mode = 0b11, debug = debug)

	def program(self, prog, offset = 0):
		"""
		Write the content of the iterable ``prog`` starting with the optional offset ``offset``
		to the device.

		Invokes write_.
		"""
		for addr, word in enumerate(prog):
			self.write(offset + addr, word)
	
	
