Quickstart
**********

Jumping into PyRegisterMachine2
===============================

The first thing you might want to do is to assemble some code and run it on the engine.
To do so you have to set up a ``Processor`` and the ``Assembler``::

	from py_register_macine2.machines.small import small_register_machine
	from py_register_machine2.tools.assembler.assembler import Assembler
	processor, rom, ram, flash = small_register_machine()
	processor.setup_done()

``small_register_machine`` returns a configured engine with 50 words ROM, 200 words RAM and 500 words Flash.
The size of a word is 64 bit.

Now you need a program, in this case we will use  simple ``Hello, World`` program::

	from io import StringIO
	asm = '''\
	ldi 'H' out0
	ldi 'e' out0
	ldi 'l' out0
	ldi 'l' out0
	ldi 'o' out0
	ldi '!' out0
	ldi 0xa out0
	ldi 0b1 ECR'''
	stream = StringIO(asm)

This will print ``Hello!\n`` to ``sys.stdout`` and stop the engine. The assembly language is KASM2.

The assembler will convert the assembly into machine code::

	assembler = Assembler(processor, stream)
	code = assembler.assemble()

The machine code is just a ``list`` of ``int`` objects that can be programmed to the
ROM or Flash device::

	rom.program(code)

And then the Processor will execute the program::

	processor.run()


Putting it all together::

	from py_register_macine2.machines.small import small_register_machine
	from py_register_machine2.tools.assembler.assembler import Assembler
	processor, rom, ram, flash = small_register_machine()
	processor.setup_done()
	from io import StringIO
	asm = '''\
	ldi 'H' out0
	ldi 'e' out0
	ldi 'l' out0
	ldi 'l' out0
	ldi 'o' out0
	ldi '!' out0
	ldi 0xa out0
	ldi 0b1 ECR'''
	stream = StringIO(asm)
	assembler = Assembler(processor, stream)
	code = assembler.assemble()
	rom.program(code)
	processor.run()


	
