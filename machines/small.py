#!/usr/bin/python3

"""
**py_register_machine2.machines.small**: a collection of small ready to use register machines


**About Register Machine Definitions**

All Register Machine Definitions are functions that take at least ``0`` arguments and return
a ``tuple`` with length ``4``: ``(Processor, ROM, RAM, Flash)``

*Example*: a simple Register Machine::

	from py_register_machine2.core import memory, processor, register, device
	from py_register_machine2.commands.basic_commands import basic_commands
	def simple_register_machine():
		rom = memory.ROM(60)
		ram = memory.RAM(70)
		flash = device.Flash(300)

		proc = processor.Processor()
		proc.register_memory_device(rom)
		proc.register_memory_device(ram)
		proc.register_device(flash)

		r0 = register.Register("r0")
		r1 = register.Register("r1")
		r2 = register.Register("r2")
		r3 = register.Register("r3")
		r4 = register.Register("r4")
		r5 = register.Register("r5")

		for reg in (r0, r1, r2, r3, r4, r5):
			proc.add_register(reg)
		for command in basic_commands:
			proc.register_command(command)

		return (proc, rom, ram, flash)
		

	
"""

from ..core import processor, memory, register, device
from ..commands.basic_commands import basic_commands
import sys

def small_register_machine(rom_size = 50, ram_size = 200, flash_size = 500):
	"""
	An unprogrammend Register Machine with 

	* one OutputRegister to ``sys.stdout`` (``out0``)
	* 15 General Purpose Register (``r0 - r14``)

	returns : ``(Processor, ROM, RAM, Flash)``
	"""
	rom = memory.ROM(rom_size)
	ram = memory.RAM(ram_size)
	flash = device.Flash(flash_size)

	proc = processor.Processor()

	proc.register_memory_device(rom)
	proc.register_memory_device(ram)
	proc.register_device(flash)

	registers = [register.OutputRegister("out0", sys.stdout),
		register.Register("r0"),
		register.Register("r1"),
		register.Register("r2"),
		register.Register("r3"),
		register.Register("r4"),
		register.Register("r5"),
		register.Register("r6"),
		register.Register("r7"),
		register.Register("r8"),
		register.Register("r9"),
		register.Register("r10"),
		register.Register("r11"),
		register.Register("r12"),
		register.Register("r13"),
		register.Register("r14")]

	for r in registers:
		proc.add_register(r)

	for command in basic_commands:
		proc.register_command(command)

	return (proc, rom, ram, flash)
