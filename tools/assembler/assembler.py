#!/usr/bin/python3

"""
**py_register_machine2.tools.assembler.assember**: The Basic Assembler

Just replaces mnemonics with opcodes and handles references.
"""

from ...engine_tools.conversions import *
import logging

# logging.basicConfig(level = logging.DEBUG)


def isreference(wordlist):
	"""
	if the line is a reference (jump mark),
	return true
	"""
	return wordlist[0].endswith(":")


class Assembler(object):
	"""
	.. _Assembler:

	Reads assembly code from ``open_stream`` and converts it to
	a ``list`` of integers that can be programmed to the ROM or the Flash.

	**Stages**:

	Split Run
		Reads the complete file and converts it to a list of tuples:
		``[(lineno, "command", <command>, arguments), ...]``` or
		``[(lineno, "data", <data description>, data), ...]```

	Argument Run
		Checks and converts the arguments. Unconvertable ``str`` objects are
		interpreted as addresses.

	Dereference Run
		Handles references.
	
	Program Run
		Generates one iterable of integers
	
	"""
	def __init__(self, processor, open_stream, directives = [], commentstarts = [";"]):
		self.processor = processor
		self.open_stream = open_stream
		self.directives = {d.name: d for d in directives}
		self.line_count = 0
		self.word_count = 0
		self.refs = {} # jump marks
		self.static_refs = {} # will stay in flash
		self.commentstarts = commentstarts

		self.commands = {}
		for opcode, command in self.processor.commands_by_opcode.items():
			self.commands[command.mnemonic()] = command
		self.register = self.processor.register_interface.registers_by_name

		self.register_indices = {}
		for index, register in enumerate(self.processor.register_interface.registers_by_index):
			self.register_indices[register.name] = index

	def split_run(self):
		"""
		.. _split_run:

		Splits the assembly code into

		* commands
		* directives
		* jump marks

		"""
		sp_run = []
		for line in self.open_stream.read().split("\n"):
			self.line_count += 1
			if(self.iscomment(line)):
				continue
			if(line.isspace()):
				continue
			line = self.stripcomments(line)

			words = line.split()
			if(len(words) == 0):
				continue
			if(isreference(words)):
				self.add_ref(words)
				continue
			if(self.isdirective(words)):
				sp_run.append(self.handle_directive(words))
				continue
			if(not words[0] in self.commands):
				raise AssembleError("[Line {}]: Unknown Mnemonic '{}'".format(self.line_count, words[0]))

			mnemo = words[0]
			args = words[1:]
			if(len(args) != self.commands[mnemo].numargs()):
				# check for default arguments
				args_ = list(args)
				for argtype in self.commands[mnemo].argtypes()[len(args):]:
					if(not argtype.can_default):
						raise AssembleError("[Line {}]: Mnemonic '{}' expects {} arguments, but got {}".format(self.line_count, mnemo, self.commands[mnemo].numargs(), len(args)))
					else:
						args_.append(argtype.default)
				args = args_
			self.word_count += 1 + len(args)
						
			logging.debug("split run: " + str((self.line_count, "command", self.commands[mnemo], (args))))
			sp_run.append((self.line_count, "command", self.commands[mnemo], (args)))
		return sp_run


	def add_ref(self, wordlist):
		"""
		Adds a reference.
		"""
		refname = wordlist[0][:-1]

		if(refname in self.refs):
			raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count, 
						refname, self.refs[refname][0], self.refs[refname][1]))
		self.refs[refname] = (self.word_count, self.line_count)


	def handle_directive(self, words):
		"""
		handles directives: adds the reference and allocates space for the content	
		"""
		refname = words[1]
		logging.debug("Handling directive " + str(self.getdirective(words[0])))
		logging.debug("First argument is " + str(words[1]))

		if(self.getdirective(words[0]).isstatic()):
			if(refname in self.static_refs):
				raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count,
							refname, self.static_refs[refname][0], self.static_refs[refname][1]))
			self.static_refs[refname] = (self.word_count, self.line_count)
		else:
			if(refname in self.refs):
				raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count,
							refname, self.refs[refname][0], self.refs[refname][1]))
			self.refs[refname] = (self.word_count, self.line_count)
		directive = self.getdirective(words[0])
		self.word_count += directive.get_word_count(words[2:])
		logging.debug("Directive allocates {} words.".format(directive.get_word_count(words[2:])))
		return (self.line_count, "data", directive, words[2:])
	def isdirective(self, words):
		"""
		Check if the line ``words`` is a directive.
		"""
		return words[0] in self.directives
	def getdirective(self, name):
		"""
		Returns the directive with the name ``name``.
		"""
		return self.directives[name]

	def argument_run(self, sp_r):
		"""
		.. _argument_run:

		Converts Arguments according to ``to_int``
		"""
		arg_run = []

		for line in sp_r:
			logging.debug("argument run: handling: " + str(line))
			if(line[1] == "data"):
				arg_run.append( (line[0], line[1], line[2], line[2].get_words(line[3])))
				continue
			if(line[1] == "command"):
				self.checkargs(line[0], line[2], line[3])
				arg_run.append( (line[0], line[1], line[2], [a for a in self.convert_args(line[2], line[3])]))
		return arg_run
				

	def checkargs(self, lineno, command, args):
		"""
		Check if the arguments fit the requirements of the command.

		Raises ArgumentError_, if an argument does not fit.
		"""
		for wanted, arg in zip(command.argtypes(), args):
			wanted = wanted.type_
			if(wanted == "register" and (not arg in self.register)):
				raise ArgumentError("[line {}]: Command '{}' wants argument of type register, but {} is not a register".format(lineno, command.mnemonic(), arg))
			if(wanted == "const" and (arg in self.register)):
				raise ArgumentError("[line {}]: Command '{}' wants argument of type const, but {} is a register.".format(lineno, command.mnemonic(), arg))

	def convert_args(self, command, args):
		"""
		Converts ``str -> int`` or ``register -> int``.
		"""

		for wanted, arg in zip(command.argtypes(), args):
			wanted = wanted.type_
			if(wanted == "const"):
				try:
					yield to_int(arg)
				except:
					if(arg in self.processor.constants):
						yield self.processor.constants[arg]
					else:
						yield arg
			if(wanted == "register"):
				yield self.register_indices[arg]

	def dereference_run(self, arg_r):
		"""
		.. _dereference_run:

		Converts the commands to opcodes and inserts the (relative or static) references.
		
		"""
		wc = 0
		der_run = []
		for line in arg_r:
			args = []
			for argument in line[3]:
				logging.debug("dereference run: handling argument " + str(argument))
				if(isinstance(argument, int)):
					logging.debug("Argument interpreted as integer")
					args.append(argument)
					continue
				if((not argument in self.refs) and 
						(not argument in self.static_refs)):
					raise ArgumentError("[line {}]: Argument '{}' is neither an int nor a reference.".format(line[0], argument))
				if(argument in self.static_refs):
					logging.debug("Argument interpreted as static reference")
					args.append(self.static_refs[argument][0])
					continue
				my_word = wc
				ref_word = self.refs[argument][0]
				args.append(ref_word - my_word)
				logging.debug("Argument interpreted as reference")
			data = []
			if(line[1] == "command"):
				data = [line[2].opcode()]
			data.extend(args)
			wc += len(data)
			der_run.append((line[0], line[1], data))
		return der_run
			


	def program_run(self, der_r):
		"""
		.. _program_run:

		Generates an iterable that can be programmed onto the register machine.
		"""

		program = []
		for line in der_r:
			program.extend(line[2])
		return program
	def assemble(self):
		"""
		.. _assembler:

		Chains split_run_, argument_run_, dereference_run_ and program_run_.
		"""

		sp_r = self.split_run()
		ar_r = self.argument_run(sp_r)
		de_r = self.dereference_run(ar_r)
		program = self.program_run(de_r)
		return program

	def iscomment(self, line):
		for commentstart in self.commentstarts:
			if(line.startswith(commentstart)):
				return True
		return False

	def stripcomments(self, line):
		for commentstart in self.commentstarts:
			if(commentstart in line):
				line = line[:line.index(commentstart)]
		return line


class ArgumentError(Exception):
	"""
	.. _ArgumentError:

	Raised if an argument does not fit the requirements.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)
class AssembleError(BaseException):
	"""
	.. _AssembleError:

	Rasied if the assemler terminates without success.
	"""
	def __init__(self, *args):
		 BaseException.__init__(self, *args)

