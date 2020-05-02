#!/usr/bin/python3

"""
**py_register_machine2.machines.small**: a collection of small ready to use register machines
	
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

def get_machine(rom_size = 50, ram_size = 200, flash_size = 500):
	proc, rom, ram, flash = small_register_machine(rom_size, ram_size, flash_size)
	proc.setup_done()
	return (proc, rom, ram, flash)

