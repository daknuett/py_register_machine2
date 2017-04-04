"""

A command line interface for py_register_machine2.

Used to compile and execute assembly code.

**Note**: The binary object code is divided into sections.
There are the following two sections:

- ``ROM`` will be programmed into the ROM
- ``FLASH`` will be programmed into the Flash

The sections are splitted by a newline character in the binary
file::

	<sectionname>:<code>

Eg::

	ROM:[22, 0, 4, 22, 1, 1]
	FLASH:[22, 0, 4, 22, 1, 1]


::

	Usage:
		cli assemble (<infile> | --string <string>) [options]
		cli execute (<infile> | --string <string>) [options]
		cli link <outfile> <linkfiles> ...

	Options:
		-c <commandmodule> --commands=<commandmodule>    use the given commands [default: py_register_machine2.commands.basic_commands]
		-m <machinemodule> --machine=<machinemodule>     use the given register machine [default: py_register_machine2.machines.small]
		-r --register-commands                           actually register the commands specified by -c
		-s <steps> --steps=<steps>                       run <steps> processor cycles, if <steps> is negative the processor will just execute all steps [default: -1]
		--commentstart=<commentstart>                    use commentstart to start comments [default: [';']]
		--string=<string>                                use the given string instead of an input file
		-o <outfile> --output=<outfile>                  write output to the given file (if unspecified write to sys.stdout)
		-S <section> --section=<section>                 the assembly code is for the given section [default: ROM]
		-v --verbose                                     add more output
		-d <debug> --debug=<debug>                       set debugging verbosity [default: 0]
		--directive-import <directivemodule>             import this module for directives [default: py_register_machine2.tools.assembler.directives]
		-D <directives> --directives=<directives>        use these directives [default: []] NOTE: all directives must be named ``directives.<Directive>``.

"""


