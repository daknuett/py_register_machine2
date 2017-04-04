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

Usage:
	cli assemble (<infile> | --string <string>) [options]
	cli execute (<infile> | --string <string>) [options]
	cli link <outfile> <linkfiles> ...

Options:
        -c <commandmodule> --commands=<commandmodule>    use the given commands [default: py_register_machine2.commands.basic_commands]
        -m <machinemodule> --machine=<machinemodule>     use the given register machine [default: py_register_machine2.machines.small]
        -r --register-commands                           actually register the commands specified by -c
        -s <steps> --steps=<steps>                       run <steps> processor cycles, if <steps> is negative the processor
	                                                 will just execute all steps [default: -1]
        --commentstart=<commentstart>                    use commentstart to start comments [default: [';']]
        --string=<string>                                use the given string instead of an input file
        -o <outfile> --output=<outfile>                  write output to the given file (if unspecified write to sys.stdout)
        -S <section> --section=<section>                 the assembly code is for the given section [default: ROM]
        -v --verbose                                     add more output
        -d <debug> --debug=<debug>                       set debugging verbosity [default: 0]
        --directive-import <directivemodule>             import this module for directives [default: py_register_machine2.tools.assembler.directives]
        -D <directives> --directives=<directives>        use these directives [default: []]
                                                         NOTE: all directives must be named ``directives.<Directive>``.
"""

import docopt, sys
from ...tools.assembler.assembler import Assembler
from io import StringIO
from importlib import import_module


def assemble(arguments):
	if(arguments["--string"]):
		infile = StringIO(arguments["--string"])
	else:
		infile = open(arguments["<infile>"])
	if("--output" in arguments and arguments["--output"]):
		outfile = open(arguments["--output"], "w")
	else:
		outfile = sys.stdout

	commands = import_module(arguments["--commands"])
	machine = import_module(arguments["--machine"])
	directives = import_module(arguments["--directive-import"])

	proc, rom, ram, flash = machine.get_machine()

	if(arguments["--register-commands"]):
		for c in commands.get_commands():
			proc.register_command(c)
	assembler = Assembler(proc, infile, 
			commentstarts = eval(arguments["--commentstart"]),
			directives = eval(arguments["--directives"]))
	section = arguments["--section"]
	print("{}:{}".format(section, assembler.assemble()), file = outfile) 

def execute(arguments):
	if(arguments["--string"]):
		infile = StringIO(arguments["--string"])
	else:
		infile = open(arguments["<infile>"])

	commands = import_module(arguments["--commands"])
	machine = import_module(arguments["--machine"])

	proc, rom, ram, flash = machine.get_machine()
	proc.debug = int(arguments["--debug"])

	if(arguments["--register-commands"]):
		for c in commands.get_commands():
			proc.register_command(c)

	sections = {"ROM": rom, "FLASH": flash}

	code = infile.read().split("\n")
	for line in code:
		if(line == ""):
			continue
		sec, co = line.split(":")
		sections[sec].program(eval(co))

	if(int(arguments["--steps"]) < 0):
		proc.run()
	else:
		for i in range(int(arguments["--steps"])):
			proc.do_cycle()

	if(arguments["--verbose"]):
		print("== registers ==")
		for k,v in sorted(proc.register_interface.registers_by_name.items()):
			print(k, "\t:", v.read())
	

def link(arguments):
	fout = open(arguments["<outfile>"], "w")

	for fname in arguments["<linkfiles>"]:
		if(arguments["--verbose"]):
			print("linking", fname)
		fin = open(fname)
		data = fin.read()
		fin.close()
		if(data[-1] != '\n'):
			print("WARNING: NOEOF line. The file might be corrupted", file = sys.stderr)
			data += '\n'
		fout.write(data)
	fout.close()
	




arguments = docopt.docopt(__doc__)

commands = {
	"assemble": assemble,
	"execute": execute,
	"link": link
}


for k, v in commands.items():
	if(arguments[k]):
		v(arguments)
