"""
Module to provide finished machines.


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
		


***Note***: All modules must provide a function ``get_machine`` 
that is a register machine definition. The processor must be 
ready-to-use. This means, that ``proc.setup_done()`` has been
invoked.
"""
