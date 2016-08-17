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


A simple Code Loader
====================

Usually the ROM will be too small to hold the programs you want to execute,
so those will be stored in the Flash.

To execute programs stored in the Flash one has to load them into RAM, this is done by the Code Loader(*CL*) or Boot Code Loader (*BCL*) stored in the ROM.

We will use the same setup like above::
	
	
	from py_register_macine2.machines.small import small_register_machine
	from py_register_machine2.tools.assembler.assembler import Assembler
	from py_register_machine2.tools.assembler.directives import ConvertingDirective
	from io import StringIO

	processor, rom, ram, flash = small_register_machine()
	processor.setup_done()

	asm = '''\
	.set flash_sec_size flash_sec_end
	ldi 'H' out0
	ldi 'e' out0
	ldi 'l' out0
	ldi 'l' out0
	ldi 'o' out0
	ldi '!' out0
	ldi 0xa out0
	ldi 0b1 ECR
	flash_sec_end:
	'''

	stream = StringIO(asm)
	
	# This directive will allow you to set one word to a special value
	# used to get the size of the section
	set_directive = ConvertingDirective(".set", lambda x: x)

	assembler = Assembler(processor, stream, directives = [set_directive])
	code = assembler.assemble()

The only new part is the size of the program, stored in the first word, now we will store the program in the Flash::

	flash.program(code)

So now we need the *CL*::

	cl = '''\
	ldi 0 r0
	in r0 r1
	ldi RAMEND_LOW r2

	loop:
	inc r0
	in r0 r3
	pst r3 r2
	inc r2
	dec r1
	jne r1 loop

	sjmp RAMEND_LOW
	'''

What does that code snippet? 

At first it reads the size of the code section in the Flash device::

	ldi 0 r0
	in r0 r1

and sets up a pointer to the RAM word to write into::

	ldi RAMEND_LOW r2

After that it copies the content from the Flash to the RAM using a do-while-loop. Finally it jumps to the first word in RAM::

	sjmp RAMEND_LOW

The constant ``RAMEND_LOW`` is a processor constant and points to the first word of the RAM.
You are able to generate jump marks using ``<name>:`` (i.e. ``loop:``).

Now you need to assemble and store the Code Loader::

	stream = StringIO(cl)
	assembler = Assembler(processor, stream)
	code = assembler.assemble()
	rom.program(code)

And run it::

	processor.run()

**Putting it all together**::

	from py_register_macine2.machines.small import small_register_machine
	from py_register_machine2.tools.assembler.assembler import Assembler
	from py_register_machine2.tools.assembler.directives import ConvertingDirective
	from io import StringIO

	processor, rom, ram, flash = small_register_machine()
	processor.setup_done()

	asm = '''\
	.set flash_sec_size flash_sec_end
	ldi 'H' out0
	ldi 'e' out0
	ldi 'l' out0
	ldi 'l' out0
	ldi 'o' out0
	ldi '!' out0
	ldi 0xa out0
	ldi 0b1 ECR
	flash_sec_end:
	'''

	stream = StringIO(asm)
	
	# This directive will allow you to set one word to a special value
	# used to get the size of the section
	set_directive = ConvertingDirective(".set", lambda x: x)

	assembler = Assembler(processor, stream, directives = [set_directive])
	code = assembler.assemble()

	flash.program(code)

	cl = '''\
	ldi 0 r0
	in r0 r1
	ldi RAMEND_LOW r2

	loop:
	inc r0
	in r0 r3
	pst r3 r2
	inc r2
	dec r1
	jne r1 loop

	sjmp RAMEND_LOW
	'''
	
	stream = StringIO(cl)
	assembler = Assembler(processor, stream)
	code = assembler.assemble()
	rom.program(code)
	processor.run()
