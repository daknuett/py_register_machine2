#!/usr/bin/python3


"""
**py_register_machine2.core.commands**: Abstract Commands
"""


class BaseCommand(object):
	"""
	The base class for Commands.

	Every Command has to be derived from BaseCommand and provide the following functions:

	* exec_
	* numargs_
	* mnemonic_
	* opcode_
	* argtypes_

	"""
	def __init__(self, mnemonic, opcode, numargs, argtypes):
		self._mnemonic = mnemonic
		self._opcode = opcode
		self._numargs = numargs
		self._argtypes = argtypes
		self.register_interface = None
		self.membus = None
		self.devbus = None

	def exec(self, *args):
		"""
		.. _exec:

		Exec will execute the Action of the Command.
		The method will be provided with numargs_ arguments and
		might read/write data via the attributes ``register_interface``,
		``membus`` and ``devbus`` provided once the Command is registered in the Processor_ 
		using register_command_.
		"""
		pass
	def numargs(self):
		"""
		.. _numargs:

		Returns the number of needed arguments.
		Used in the ``fetch-operands-phase``.
		"""
		return self._numargs
	def mnemonic(self):
		"""
		.. _mnemonic:

		Returns the mnemonic of the command (``str``).
		Used by the Assembler and Disassembler.
		"""
		return self._mnemonic
	def opcode(self):
		"""
		.. _opcode:

		Returns the opcode of the command (``int``).
		Used by the Assembler and in the ``decode-command-phase``.
		"""
		return self._opcode

	def argtypes(self):
		"""
		.. _argtypes:

		Return a list of strings defining the argument types,
		i.e.::

			["register", "register"]
		"""
		return self._argtypes

class ArgumentType(object):
	"""
	.. _ArgumentType:

	Represents argument types. Actually there are only the types
	``"register"`` and ``"const"`` but it might be helpful to 
	use default values. Those are stored in the ArgumentType, too.

	This module provides the functions ``registerargument()`` and
	``constargument()`` those will return an ``ArgumentType(type_ = "register", can_default = False, default = 0)``
	and an ``ArgumentType(type_ = "const", can_default = False, default = 0)``
	"""
	def __init__(self, type_ = "register", can_default = False, default = 0):
		self.type_ = type_
		self.can_default = can_default
		self.default = default
	def __repr__(self):
		return "ArgumentType(type_ = {}, can_default = {}, default = {})".format(repr(self.type_),
				self.can_default, repr(self.default))
def registerargument():
	return ArgumentType(type_ = "register", can_default = False, default = 0)
def constargument():
	return ArgumentType(type_ = "const", can_default = False, default = 0)

class ArithmeticCommand(BaseCommand):
	"""
	.. _ArithmeticCommand:

	Used for calculation commands, ``numargs`` is always 2,
	both arguments are Registers.

	*Example*: The ``add`` command::

		add_function = lambda a,b: a+b
		add_command = ArithmeticCommand("add", 2, add_function)

	
	"""
	def __init__(self, mnemonic, opcode, function):
		BaseCommand.__init__(self, mnemonic, opcode, 2, [registerargument(), registerargument()])
		self.function = function

	def exec(self, operand1, operand2):
		"""
		Uses two operands and performs a function on their content.::

			operand1 = function(operand1, operand2)
		"""
		in1 = self.register_interface.read(operand1)
		in2 = self.register_interface.read(operand2)
		out = self.function(in1, in2)
		self.register_interface.write(operand2, out)

class FunctionCommand(BaseCommand):
	"""
	.. _FunctionCommand:

	Provides a basic handle to create Commands.

	The argument ``function`` is a function with at least three arguments:

	1. ``register_interface``
	2. ``memory_BUS``
	3. ``device_BUS``

	The function will be able to access the Processor's RegisterInterface_ and BUS_ es
	through this arguments.

	If the function needs any operands the number of additional arguments have to be
	in ``numargs``

	For arithmetic commands (like ``add``, ``mul``,...) see ArithmeticCommand_.

	*Example*: ``ld`` Command::

		def ld_function(register_interface, memory_BUS, device_BUS, addr_from, to):
			from_ = register_interface.read(addr_from)

			word = memory_BUS.read_word(from_)
			register_interface.write(to, word)
		
		ld_command = FunctionCommand("ld", 34, 2, ld_function, ["const", "register"])
			
	*Example*: ``nop`` Command::

		def nop_function(register_interface, memory_BUS, device_BUS):
			return
		nop_command = FunctionCommand("nop", 36, 0, nop_function, [])
			
	"""
	def __init__(self, mnemonic, opcode, numargs, function, argtypes):
		BaseCommand.__init__(self, mnemonic, opcode, numargs, argtypes)
		self.function = function

	def exec(self, *args):
		self.function(self.register_interface, self.membus, self.devbus, *args)

