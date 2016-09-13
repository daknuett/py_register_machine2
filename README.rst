py_register_machine2
********************
A Register Machine package for Python3


You might take a look at the `docs<https://daknuett.github.io/py_register_machine2>` for a lot information about design, usage and the complete code documentation.

Installation of version 0.0.1 via ``pip``::
	
	python3 -m pip install py_register_machine2

Basic Usage
-----------

Basically you need to perform at least three steps:

0. (optional) Write and Assemble Code
1. Generate a engine (Processor, Rom, [Ram], [Flash])
2. Program the engine (Programming the Rom [and the Flash])
3. Start the engine (``Processor.run()``)

Eg.::

	from py_register_macine2.machines.small import small_register_machine
	from py_register_machine2.tools.assembler.assembler import Assembler
	from io import StringIO

	processor, rom, ram, flash = small_register_machine()
	processor.setup_done()

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

You are able to write machine code using ``list`` objects. The ``Assemmbler.assembler()`` returns such a list.
	
`See Also<https://daknuett.github.io/py_register_machine2/quickstart.html>`
