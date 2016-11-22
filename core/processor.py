#!/usr/bin/python3
from ..core import memory, device, register
import time


"""
**py_register_machine2.core.processor**: The processor and his parts
"""

class EnigneControlBits(object):
	"""
	.. _EnigneControlBits:

	Container for the static engine controll bits.
	Used by the Processor_ to handle his ECR.
	"""
	engine_stop_bit = 0b00000001



class RegisterInterface(object):
	"""
	.. _RegisterInterface:

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
		.. _add_register:

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
		"""
		Write a word in the Register with the name ``name_or_index`` or with the index ``name_or_index``.
		``name_or_index`` hat to be either ``str`` or ``int``. If the type of ``name_or_index``
		is wrong an AttributeError will be raised.

		If there is no Register with the specified name or index, a NameError will be raised.
		"""
		if(isinstance(name_or_index, str)):
			if(name_or_index in self.registers_by_name):
				self.registers_by_name[name_or_index].write(word)
			else:
				raise NameError("No Register with name '{}'".format(name_or_index))
		elif( isinstance(name_or_index, int)):
			if(name_or_index < len(self.registers_by_index)):
				self.registers_by_index[name_or_index].write(word)
			else:
				raise NameError("No Register with index '{}'".format(name_or_index))
		else:
			raise AttributeError("name_or_index has to be `str` or `int`, but is {}".format(type(name_or_index)))

	def read(self, name_or_index):
		"""
		Read a word from the Register with the name ``name_or_index`` or with the index ``name_or_index``.
		``name_or_index`` hat to be either ``str`` or ``int``. If the type of ``name_or_index``
		is wrong an AttributeError will be raised.

		If there is no Register with the specified name or index, a NameError will be raised.
		"""
		if(isinstance(name_or_index, str)):
			if(name_or_index in self.registers_by_name):
				return self.registers_by_name[name_or_index].read()
			else:
				raise NameError("No Register with name '{}'".format(name_or_index))
		elif( isinstance(name_or_index, int)):
			if(name_or_index < len(self.registers_by_index)):
				return self.registers_by_index[name_or_index].read()
			else:
				raise NameError("No Register with index '{}'".format(name_or_index))
		else:
			raise AttributeError("name_or_index has to be `str` or `int`, but is {}".format(type(name_or_index)))


class Processor(object):
	"""
	.. _Processor:

	Fetches Opcodes from the ROM or RAM, decodes them and executes the commands.


	.. _processor_phases:

	Phases in one operation cycle:

	Fetch Phase
		The Processor fetches the Opcode (one word) from the ROM or RAM device
		according to the program counter and increases the program counter.
	Decode Phase
		The Processor looks up the Command to execute
	Fetch Operands Phase
		(optional) If requested the processor fetches the operands and increases the program counter.
	Execute Phase
		The Processor executes the Command.
	Write Back Phase
		(optional) If there is a result this result is written to a register or the RAM or a device.


	**Special Register**

	.. _PC:

	.. _ECR:

	.. _SP:

	0. The first Register (index 0) is the Program Counter(PC).
	1. The second Register (index 1) is the Engine Control Register (ECR) take a look at EnigneControlBits_.
	2. The third Register (index 2) is the Stack Pointer (SP) and may be used for ``call``, ``ret``, ``push`` and ``pop``


	.. _`internal constants`:

	**Internal Constants**

	Constants used by the Assembler, should be set using setup_done_
	
	``ROMEND_LOW``
		First word of the ROM_ (always ``0``)
	``ROMEND_HIGH`` 
		Last word of the ROM_
	``RAMEND_LOW``
		First word of the RAM_, (``ROMEND_HIGH + rom.size``)
	``RAMEND_HIGH``
		Last word of the RAM_
	``FLASH_START``
		First word of the Flash_(always ``0``)
	``FLASH_END``
		Last word of the Flash_
	*Interrupt Name*
		Address of the interrupt (set by invoking ``add_interrupt``)

	**Cycles**
	
	The number of cycles can be observed by acessing the ``cycles`` variable.

	"""
	def __init__(self, f_cpu = None, width = 64,
			interrupts = False, clock_barrier = None, debug = 0):
		self.memory_bus = memory.BUS(width = width, debug = debug)
		self.device_bus = device.BUS(width = width, debug = debug)
		self.register_interface = RegisterInterface(width = width, debug = debug)
		# program counter, engine control register, stack pointer
		self.register_interface.add_register(register.Register("PC", width = width))
		self.register_interface.add_register(register.Register("ECR", width = width))
		self.register_interface.add_register(register.Register("SP", width = width))
		self.f_cpu = f_cpu
		self.clock_barrier = clock_barrier

		if(f_cpu != None and clock != None):
			raise SetupError("Software Clock (f_cpu) and Thread Clock (clock_barrier) are mutually exclusive")
		self.interrupt_enable = interrupts
		self.interrupts = []
		self.debug = debug

		self.commands_by_opcode = {}

		self.last_cycle = None
		self.current_cycle = None


		self.pc = 0
		self.ecr = 0
		self.sp = 0
		self.on_cycle_callbacks = []
		self.constants = {}
		self.cycles = 0
		self.push_pc = False

	def en_dis_able_interrupts(self, mask):
		"""
		This callback might be used by a Register to enable/disable Interrupts.

		``mask`` is an ``int``, the Interrupts are bits in this mask, the first registered interrupt
		has the bit ``(1 << 0)``, the n-th Interrupt the bit ``(1 << (n - 1))``.
		If the bit is cleared (``0``) the Interrupt will be disabled.
		"""
		for shift, interrupt in enumerate(self.interrupts):
			if(mask & (1 << shift)):
				interrupt.enable = True
			else:
				interrupt.enable = False
	def add_interrupt(self, interrupt):
		"""
		Adds the interrupt to the internal interrupt storage ``self.interrupts`` and
		registers the interrupt address in the internal constants.
		"""
		self.interrupts.append(interrupt)
		self.constants[interrupt.name] = interrupt.address
	def interrupt(self, address):
		"""
		Interrupts the Processor and forces him to jump to ``address``.
		If ``push_pc`` is enabled this will push the PC to the stack.
		"""
		if(self.push_pc):
			self.memory_bus.write_word(self.sp, self.pc)
			self._set_sp(self.sp - 1)
		self._set_pc(address)

	def _increase_pc(self):
		self.pc += 1
		self.register_interface.write(0, self.pc)
		self.pc = self.register_interface.read(0)
	def _refresh_pc(self):
		self.pc = self.register_interface.read(0)
	def _refresh_ecr(self):
		self.ecr = self.register_interface.read(1)
		if(self.debug > 5):
			print("ECR: {}".format(bin(self.ecr)))
	def _refresh_sp(self):
		self.sp = self.register_interface.read(2)
	def _fetch_at_pc(self):
		opcode = self.memory_bus.read_word(self.pc)
		self._increase_pc()
		return opcode
	def _set_sp(self, sp):
		self.sp = sp
		self.register_interface.write(2, sp)
		self._refresh_sp()
	def _set_pc(self, pc):
		self.pc = pc
		self.register_interface.write(0, pc)
		self._refresh_pc()
	def _set_ecr(self, ecr):
		self.ecr = ecr
		self.register_interface.write(1, ecr)
		self._refresh_ecr()
	def _execute_on_cycle_callbacks(self):
		for callback in self.on_cycle_callbacks:
			callback()
	def setup_done(self):
		"""
		.. _setup_done:
	
		Finish the setup of the Processor.

		This should be the last call before the Processor is used.
		Sets the `internal constants`_ (used by the assembler) and
		sets the Stack Pointer to RAMEND_HIGH, if there is a RAM attached.
		If there is no RAM attached, SP will stay ``0``.

		If there is a RAM attached ``push_pc`` is set.

		Might raise SetupError_.
		"""
		if(self.memory_bus.device_count() < 1):
			raise SetupError("At least a ROM device has to be attached.")

		rom = self.memory_bus.devices[0]
		self.constants["ROMEND_HIGH"] = rom.size - 1
		self.constants["ROMEND_LOW"] = 0

		if(self.memory_bus.device_count() > 1):
			ram = self.memory_bus.devices[1]
			self.constants["RAMEND_HIGH"] = rom.size + ram.size - 1
			self.constants["RAMEND_LOW"] = rom.size
			self._set_sp(rom.size + ram.size - 1)
			self.push_pc = True
		if(self.device_bus.device_count() > 0):
			flash = self.device_bus.devices[0]
			self.constants["FLASH_START"] = 0
			self.constants["FLASH_END"] = flash.size - 1
	def reset(self):
		"""
		Resets the control registers of the Processor_(PC_, ECR_ and SP_)
		"""
		rom = self.memory_bus.devices[0]
		if(self.memory_bus.device_count() > 1):
			ram = self.memory_bus.devices[1]
			self._set_sp(rom.size + ram.size - 1)
		self._set_pc(0)
		self._set_ecr(0)
		self.cycles = 0
			

	def register_on_cycle_callback(self, callback):
		"""
		A on cycle callback is executed in every clock cycle of the
		Processor. No on cycle callback modifies the state of the Processor directly,
		but it might cause an Interrupt.

		The on cycle callback is a function without arguments::

			def on_cycle_callback():
				print("One cycle done")

		The return value of a callback is ignored and the callback must not raise Exceptions,
		but fatal Errors may stop the engine.
		"""
		self.on_cycle_callbacks.append(callback)
	def register_command(self, command):
		"""
		.. _register_command:

		Register a Command in the Processor,
		the Command can now be executed by the Processor.
		"""
		if(command.opcode() in self.commands_by_opcode):
			raise SetupError("Command with opcode {}(mnemonic: {}) already registered".format(command.opcode(), command.mnemonic()))
		command.membus = self.memory_bus
		command.devbus = self.device_bus
		command.register_interface = self.register_interface
		self.commands_by_opcode[command.opcode()] = command

	def register_memory_device(self, device):
		"""
		Registers a device in the memory BUS_.

		Invokes register_device_.
		"""
		self.memory_bus.register_device(device)

	def register_device(self, device):
		"""
		Registers a device in the device BUS_.

		Invokes register_device_.
		"""
		self.device_bus.register_device(device)

	def add_register(self, register):
		"""
		Adds a new register in the RegisterInterface_.

		Invokes add_register_.
		"""
		self.register_interface.add_register(register)


	def do_cycle(self):
		"""
		.. _do_cycle:

		Run one clock cycle of the Processor_,
		works according to processor_phases_.

		Then all ``on_cycle_callbacks`` are executed and the internal Registers are updated.

		If ``f_cpu`` is set and the execution took not long enough,
		``do_cycle`` will wait until the right time for the next cycle.

		If ``clock_barrier`` is set, ``do_cycle`` will perform the ``clock_barrier.wait()``.

		Might raise SIGSEGV_, if there is an invalid opcode.
		"""
		if(self.f_cpu != None):
			if(self.last_cycle == None):
				self.last_cycle = time.time()

		opcode = self._fetch_at_pc()
		if(not opcode in self.commands_by_opcode):
			raise SIGSEGV("Invalid opcode ({}) at {}".format(opcode, self.pc - 1))
		command = self.commands_by_opcode[opcode]
		numargs = command.numargs()
		args = [self._fetch_at_pc() for i in range(numargs)]
		if(self.debug > 2):
			print("{}|EXEC: [{}] {} $ ".format(self.pc, opcode, command.mnemonic()), *args)
		command.exec(*args)

		self._refresh_pc()
		self._refresh_ecr()
		self._refresh_sp()
		self._execute_on_cycle_callbacks()

		self.current_cycle = time.time()
		if(self.f_cpu != None):
			cycle_time = self.current_cycle - self.last_cycle
			if(cycle_time < ( 1 / self.f_cpu)):
				time.sleep(( 1 / self.f_cpu) - cycle_time )
			self.last_cycle = time.time()
		if(self.clock_barrier != None):
			self.clock_barrier.wait()
		self.cycles += 1
	def run(self):
		"""
		Runs do_cycle_, until either a stop bit in the ECR_ is set (see EnigneControlBits_),
		or if an Exception in do_cycle_ occurs.
		"""
		while(1):
			self.do_cycle()
			if(self.ecr & EnigneControlBits.engine_stop_bit):
				break

		

class SetupError(Exception):
	"""
	.. _SetupError:
	
	Raised if the setup is invalid.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)


class SIGSEGV(Exception):
	"""
	.. _SIGSEGV:
	
	Raised if an invalid memory command or opcode occurs.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)
