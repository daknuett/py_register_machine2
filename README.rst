py_register_machine2
********************
A Register Machine package for Python3


You might take a look at the `docs <https://daknuett.github.io/py_register_machine2>`_ for a lot information about design, usage and the complete code documentation.


Installing PyRegisterMachine2
=============================

``py_register_machine2`` is a python3 package, so all you need to do is to place the project folder in your
``$PYTHONPATH``. You are able to get the pythonpath using ``echo $PYTHONPATH`` and ``python3 -c "import sys; print(sys.path)"``.

So you are able to install the package using::

	cd /usr/local/lib/python3.5/dist-packages/
	git clone https://github.com/daknuett/py_register_machine2

Or::

	python3 -m pip install py_register_machine2

Using PyRegisterMachine2
========================

Using Prepared Machines
-----------------------

In ``py_register_machine2.machines`` is a bunch of modules providing a bunch of  *register machine definitions* 
those are functions returning a 4-tuple: ``(processor, rom, ram, flash)``, maybe you need to invoke ``processor.setup_done()``.

Creating Your Own Machines
--------------------------

If the prepared machines do  not match your requirements you might want to create your own machines,
to do so you should study the `docs here <https://daknuett.github.io/py_register_machine2/machines.html>`_.

Instructionset, Machinecode and Assembly
----------------------------------------

The Instructionset of a machine is defined by obhects inherited from ``py_register_machine2.core.commands.BaseCommand``,
a bunch of ready-to-use commands is in ``py_register_machine2.commands``.

The processor reads one word of data for the opcode, decodes this opcode and reads n words of data for n arguments.
Machinecode can be witten using ``list`` objects like this::

	program = [0x16, 0x01, 0x01] # using the py_register_machine2.commands.basic_commands instructionset
	# this equals "ldi 0x01 ECR" and will halt the engine.

This machinecode can be programmed to a persistent device (ROM or Flash) using ::

	rom.program(program)
	# or
	flash.program(program)

There is a basic Assembler in ``py_register_machine2.tools.assembler.assembler`` that uses the KASM2 assembly language to generate
machiecode ( a ``list`` object)

The Assembler uses a configured Processor and an open stream to generate the machinecode::

	from io import StringIO
	processor.setup_done()
	progstr = "ldi 0x01 ECR"
	asm = Assembler(processor, StringIO(progstr))
	program = asm.assemble()

Once the ROM is programmed (the Processor starts executing code in the ROM) you are able to run the code using::

	processor.run()



