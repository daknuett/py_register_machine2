#!/usr/bin/python3

"""
A register machine compatible to the schedule of the bavarian gymnasium.

Differences:

* Register names are ``rX`` instead of ``X`` (i.e. ``r5`` instead of ``5``)
* The *Program Counters* are unused
* Comments start with ``;`` instead of ``--``. (see this_)

**Examples**

Old style::

	0: DLOAD 1 -- load stuff
	1: STORE 1 -- store stuff
	2: DLOAD 5
	3: SUB 1
	4: HALT

New style::

	DLOAD 1 ; load stuff
	; comments can take a complete line
	; store stuff
	STORE r1
	DLOAD 5
	SUB r1
	HALT

.. _this:

*Note*:

You are able to change the commentstart strings using the argument ``commentstarts``::

	asm = Assembler(processor, stream, commentstarts = ["--"])
"""
from py_register_machine2.core import memory, processor, register, device
from py_register_machine2.commands.gym_bav_16 import commands

def machine(romsize = 200, numregister = 15):
	rom = memory.ROM(romsize)
	proc = processor.Processor()
	proc.register_memory_device(rom)
	akk = register.Register("A")
	proc.add_register(akk)
	registers = [register.Register("r" + str(regindex)) for regindex in range(numregister)]
	for reg in registers:
		proc.add_register(reg)
	for com in commands:
		proc.register_command(com)
	proc.setup_done()
	return (proc, rom, None, None)

