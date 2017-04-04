Apps
****

Webapp
======

The goal of this package is to provide a Web Application for PRM2.
This will allow one to 

- Use a GUI
- Provide others (i.e. students) with a simple way to run KASM2 code.

Documentation
-------------

.. automodule:: py_register_machine2.app.web.front
   :members:
.. automodule:: py_register_machine2.app.web.model
   :members:

Command Line Interface
======================

The command line interface is the preferred way to use PRM2 
as a program.

Because PRM2 is way more generic the interface cannot follow
usual interface standards, like the GCC does. It is however
possible to use the CLI with make.

Using the CLI
-------------

The CLI uses three commands:

assemble
	Takes exactly one ``kasm2`` file suitable for the
	machine definition and compiles it to `prm2bin`_
	code.
link
	Takes one or more `prm2bin`_ files and concatenates
	them to one. This is actually an equivalent to ``cat
	<linkfiles> > <outfile>``, but further versions
	might provide more functions.
execute
	Executes one `prm2bin`_ file.

.. _prm2bin:

About prm2bin
-------------

prm2bin is a human readable format to store binary data. One
prm2bin file is divided into several sections (usually 2)
that will used to program the corresponding devices. The
sections are ended by a newline character (``\n``). The file
looks like this::

	<sectionname>:<content>
	<sectionname>:<content>

For instance::

	ROM:[22, 72, 3, 22, 101, 3, 22, 108, 3, 22, 108, 3, 22, 111, 3, 22, 33, 3, 22, 10, 3, 22, 1, 1]
	FLASH:[22, 1, 1]

The content is a list with the values of the words. It is
possible to modify these files using a common text editor.

Example
-------

This is a small example about how to use the CLI with GNU
make.

Makefile::
	
	asm = python3 -m py_register_machine2.app.cli assemble 
	link = python3 -m py_register_machine2.app.cli link
	execute = python3 -m py_register_machine2.app.cli execute

	asmflag = --directives="[directives.ConvertingDirective('.set', lambda x: x)]" -o

	exec: main.prm2bin
		$(execute) main.prm2bin 

	execv: main.prm2bin
		$(execute) main.prm2bin -v

	rom.prm2bin:rom.kasm2
		$(asm) rom.kasm2 --section=ROM $(asmflag) rom.prm2bin

	flash.prm2bin:flash.kasm2
		$(asm) flash.kasm2 --section=FLASH $(asmflag) flash.prm2bin

	main.prm2bin:rom.prm2bin flash.prm2bin
		$(link) main.prm2bin rom.prm2bin flash.prm2bin


	clean:
		-rm *.prm2bin

rom.kasm2::

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


flash.kasm2::

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


Documentation
-------------

.. automodule:: py_register_machine2.app.cli
   :members:

