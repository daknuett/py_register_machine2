#!/urb/bin/python3

"""
**py_register_machine2.tools.assembler.assember**: The Basic Assembler

Just replaces mnemonics with opcodes and handles references.
"""


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
	def __init__(self, processor, open_stream, directives = []):
		self.processor = processor
		self.open_stream = open_stream
		self.directives = directives
		self.line_count = 0
		self.word_count = 0
		self.refs = {} # jump marks
		self.static_refs = {} # will stay in flash

		self.commands = {}
		for opcode, command in self.processor.commands_by_opcode.items():
			self.commands[command.mnemonic()] = command
		self.register = self.processor.register_interface.registers_by_name

		self.register_indices = {}
		for index, register in enumerate(self.processor.register_interface.registers_by_index):
			self.register_indices[register.name] = index

	def split_run(self):
		sp_run = []
		for line in self.open_stream.read().split("\n"):
			self.line_count += 1
			if(line.isspace()):
				continue
			
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
				raise AssembleError("[Line {}]: Mnemonic '{}' expects {} arguments, but got {}".format(self.line_count,
							mnemo, self.commands[mnemo].numargs(), len(args)))
			sp_run.append((self.line_count, "command", self.commands[mnemo], (args)))
		return sp_run


	def add_ref(self, wordlist):
		refname = wordlist[0][:-1]

		if(refname in self.refs):
			raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count, 
						refname, self.refs[refname][0], self.refs[refname][1]))
		self.refs[refname] = (self.word_count, self.line_count)


	def handle_directive(self, words):
		refname = words[1]

		if(self.getdirective(words[0]).is_static()):
			if(refname in self.static_refs):
				raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count,
							refname, self.static_refs[refname][0], self.static_refs[refname][1]))
			self.static_refs[refname] = (self.word_count, self.line_count)
		else:
			if(refname in self.refs):
				raise ReferenceError("[line {}]:{} already defined here (word) {} (line) {}".format(self.line_count,
							refname, self.refs[refname][0], self.refs[refname][1]))
			self.refs[refname] = (self.word_count, self.line_count)
		return (self.line_count, "data", (self.getdirective(words[0]), words[1:]))
	def isdirective(self, words):
		for directive in self.directives:
			if(words[0] == directive.name):
				return True
		return False

	def argument_run(self, sp_r):
		"""
		.. _argument_run:

		Splits the code into Directives and commands and registers references.
		"""
		arg_run = []

		for line in sp_r:
			if(line[1] == "data"):
				arg_run.append( (line[0], line[1], line[2], line[2].getwords(line[3])))
				continue
			if(line[1] == "command"):
				self.checkargs(line[0], line[2], line[3])
				arg_run.append( (line[0], line[1], line[2], [a for a in self.convert_args(line[2], line[3])]))
		return arg_run
				

	def checkargs(self, lineno, command, args):
		"""
		Check if the arguments fit the requerements of the command.

		Raises ArgumentError_, if an argument does not fit.
		"""
		for wanted, arg in zip(command.argtypes(), args):
			if(wanted == "register" and (not arg in self.register)):
				raise ArgumentError("[line {}]: Command '{}' wants argument of type register, but {} is not a register".format(lineno, command.name, arg))
			if(wanted == "const" and (arg in self.register)):
				raise ArgumentError("[line {}]: Command '{}' wants argument of type const, but {} is a register.".format(lineno, command.name, arg))

	def convert_args(self, command, args):
		"""
		Converts ``str -> int`` or ``register -> int``.
		"""

		for wanted, arg in zip(command.argtypes(), args):
			if(wanted == "const"):
				try:
					yield self.to_int(arg)
				except:
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
			if(line[1] == "command"):
				args = []
				for argument in line[3]:
					if(isinstance(argument, int)):
						args.append(argument)
						continue
					if((not argument in self.refs) or 
							(not argument in self.static_refs)):
						raise ArgumentError("[line {}]: Argument '{}' is neither an int nor a reference.".format(line[0], argument))
					if(argument in self.static_refs):
						args.append(self.static_refs[argument][0])
						continue
					my_word = wc
					ref_word = self.refs[argument][0]
					args.append(ref_word - my_word)
				data = [line[2].opcode()]
				data.extend(args)
				wc += len(data)
				der_run.append((line[0], line[1], data))
				continue
			if(line[1] == "data"):
				wc += len(line[3])
				der_run.append((line[0], line[1], line[3]))
		return der_run
			

	def to_int(self, argument):
		if(argument.startswith("0b")):
			return int(argument[2:], 2)
		elif(argument.startswith("0x")):
			return int(argument[2:], 16)
		elif(argument.startswith("0") and argument != "0"):
			return int(argument[1:], 8)
		elif(argument[0] == "'" and argument[2] == "'"):
			return ord(argument[1])
		return int(argument)

	def program_run(self, der_r):
		"""
		.. _program_run:

		Generates an iterable that can be programmed onto the register machine.
		"""

		program = []
		for line in der_r:
			program.extend(line[2])
		return program

class ArgumentError(Exception):
	"""
	.. _ArgumentError:

	Raised if an argument does not fit the requirements.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)
