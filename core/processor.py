#!/usr/bin/python3


"""
**py_register_machine2.core.processor**: The processor and his parts
"""

class RegisterInterface(object):
	"""
	Used by the Processor to perform read/write
	operations on the registers.
	"""
	def __init__(self, registers = [], debug = 0, width = 64):
		self.debug = 0
		self.registers_by_name = {}
		self.registers_by_index = []
		self.width = width
		self.size = 2 ** width - 1
		self._lock = False
		for register in registers:
			self.add_register(register)

	def add_register(self, register):
		"""
		Adds the Register_ ``register`` to the interface.

		Will raise a SetupError_ if the interface is locked (because it is running) or if
		there is already a Register with the name of the new Register or if
		the number of Registers would exceed the size of the interface.

		Returns the index of the new Register
		"""
		if(self._lock):
			raise SetupError("RegisterInterface is already running, no changes to the register layout can be performed")
		if(len(self.registers_by_index) >= self.size):
			raise SetupError("Number of Registers would exceed the address space({})".format(self.size))
		if(register.name in self.registers_by_name):
			raise SetupError("Register with name '{}' already added.".format(register.name))
		self.registers_by_name[register.name] = register
		self.registers_by_index.append(register)
		return len(self.registers_by_index) - 1

	def write(self, name_or_index, word):
		pass
	def read(self, name_or_index):
		pass

class SetupError(Exception):
	"""
	.. _SetupError:
	
	raised if the setup is invalid.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)

