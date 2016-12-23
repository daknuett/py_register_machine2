#!/usr/bin/python3


"""
**py_register_machine2.commands.basic_commands**: The most important commands

+----------+--------+---------------------------------------------------+
| mnemonic | opcode | Description 					|
+==========+========+===================================================+
| mov a b  | 0x01   | copy content from register a to register b [1]_   |
+----------+--------+---------------------------------------------------+
| pld a b  | 0x02   | load from address in register a to register b [1]_|
+----------+--------+---------------------------------------------------+
| pst a b  | 0x03   | store register a to address in register b [1]_    |
+----------+--------+---------------------------------------------------+
| ld  a b  | 0x04   | load from a into register b [1]_		        |
+----------+--------+---------------------------------------------------+
| st  a b  | 0x05   | store from register a to address b [1]_	        |
+----------+--------+---------------------------------------------------+
| add a b  | 0x06   | b = a + b					        |
+----------+--------+---------------------------------------------------+
| sub a b  | 0x07   | b = a - b					        |
+----------+--------+---------------------------------------------------+
| mul a b  | 0x08   | b = a * b					        |
+----------+--------+---------------------------------------------------+
| div a b  | 0x09   | b = a / b (integer division)		        |
+----------+--------+---------------------------------------------------+
| jmp a    | 0x0a   | pc = pc + a - 2 [3]_			        |
+----------+--------+---------------------------------------------------+
| in a b   | 0x0b   | read from address in register a to register b [2]_|
+----------+--------+---------------------------------------------------+
| out a b  | 0x0c   | write register a to address in register b [2]_    |
+----------+--------+---------------------------------------------------+
| inc a    | 0x0d   | increase register a			        |
+----------+--------+---------------------------------------------------+
| dec a    | 0x0f   | decrease register a			        |
+----------+--------+---------------------------------------------------+
| jne a b  | 0x10   | if a != 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| jeq a b  | 0x11   | if a == 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| jle a b  | 0x12   | if a <= 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| jlt a b  | 0x13   | if a < 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| jge a b  | 0x14   | if a >= 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| jgt a b  | 0x15   | if a > 0: pc += b - 3			        |
+----------+--------+---------------------------------------------------+
| ldi a b  | 0x16   | Load immediate a into Register b		        |
+----------+--------+---------------------------------------------------+
| sjmp a   | 0x17   | pc = a - 2 [3]_     			        |
+----------+--------+---------------------------------------------------+

.. [1] stores and loads to/from the memory BUS
.. [2] reads and writes from/to the device BUS
.. [3] both the fetch opcode and fetch arguments increases the PC, so we need to undo this.

A list of all commands is ``basic_commands``.

"""


from ..core.commands import *

mov_function = lambda a,b: a
mov = ArithmeticCommand("mov", 0x01, mov_function)

def pld_function(register_interface, memory_BUS, device_BUS, addr_from, to):
	from_ = register_interface.read(addr_from)

	word = memory_BUS.read_word(from_)
	register_interface.write(to, word)

pld = FunctionCommand("pld", 0x02, 2, pld_function, [registerargument(), registerargument()])

def pst_function(register_interface, memory_BUS, device_BUS, from_, addr_to):
	to = register_interface.read(addr_to)

	word = register_interface.read(from_)
	memory_BUS.write_word(to, word)

pst = FunctionCommand("pst", 0x03, 2, pst_function, [registerargument(), registerargument()])


def ld_function(register_interface, memory_BUS, device_BUS, from_, to):
	word = memory_BUS.read_word(from_)
	register_interface.write(to, word)

ld = FunctionCommand("ld", 0x04, 2, ld_function, [constargument(), registerargument()])

def st_function(register_interface, memory_BUS, device_BUS, from_, to):
	word = register_interface.read(from_)
	memory_BUS.write_word(to, word)

st = FunctionCommand("st", 0x05, 2, st_function, [registerargument(), constargument()])


add_function = lambda a,b: a + b
sub_function = lambda a,b: a - b
mul_function = lambda a,b: a * b
div_function = lambda a,b: a // b

add = ArithmeticCommand("add", 0x06, add_function)
sub = ArithmeticCommand("sub", 0x07, sub_function)
mul = ArithmeticCommand("mul", 0x08, mul_function)
div = ArithmeticCommand("div", 0x09, div_function)

def jmp_function(register_interface, memory_BUS, device_BUS, to):
	pc = register_interface.read(0)
	pc -= 2
	pc += to
	register_interface.write(0, pc)
jmp = FunctionCommand("jmp", 0x0a, 1, jmp_function, [constargument()])

def sjmp_function(register_interface, memory_BUS, device_BUS, to):
	pc = to
	register_interface.write(0, pc)
sjmp = FunctionCommand("sjmp", 0x17, 1, sjmp_function, [constargument()])

def inc_function(register_interface, memory_BUS, device_BUS, register):
	word = register_interface.read(register)
	word += 1
	register_interface.write(register, word)
def dec_function(register_interface, memory_BUS, device_BUS, register):
	word = register_interface.read(register)
	word -= 1
	register_interface.write(register, word)

inc = FunctionCommand("inc", 0x0d, 1, inc_function, [registerargument()])
dec = FunctionCommand("dec", 0x0f, 1, dec_function, [registerargument()])


def branch_function(register_interface, memory_BUS, device_BUS, op1, op2, function):
	word = register_interface.read(op1)
	if(function(word)):
		pc = register_interface.read(0)
		pc += op2 - 3
		register_interface.write(0, pc)

jne_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x != 0)

jeq_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x == 0)
jle_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x <= 0)
jlt_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x < 0)
jge_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x >= 0)
jgt_function = lambda register_interface, memory_BUS, device_BUS, op1, op2: branch_function(register_interface, memory_BUS, device_BUS, op1, op2, lambda x: x > 0)

jne = FunctionCommand("jne", 0x10, 2, jne_function, [registerargument(), constargument()])
jeq = FunctionCommand("jeq", 0x11, 2, jeq_function, [registerargument(), constargument()])
jle = FunctionCommand("jle", 0x12, 2, jle_function, [registerargument(), constargument()])
jlt = FunctionCommand("jlt", 0x13, 2, jlt_function, [registerargument(), constargument()])
jge = FunctionCommand("jge", 0x14, 2, jge_function, [registerargument(), constargument()])
jgt = FunctionCommand("jgt", 0x15, 2, jgt_function, [registerargument(), constargument()])



def in_function(register_interface, memory_BUS, device_BUS, addr_from, to):
	from_ = register_interface.read(addr_from)

	word = device_BUS.read_word(from_)
	register_interface.write(to, word)


in_ = FunctionCommand("in", 0x0b, 2, in_function, [registerargument(), registerargument()])

def out_function(register_interface, memory_BUS, device_BUS, from_, addr_to):
	to = register_interface.read(addr_to)

	word = memory_BUS.read_word(from_)
	device_BUS.write_word(to, word)

out = FunctionCommand("out", 0x0c, 2, out_function, [registerargument(), registerargument()])

def ldi_function(register_interface, memory_BUS, device_BUS, const, to):
	register_interface.write(to, const)
ldi = FunctionCommand("ldi", 0x16, 2, ldi_function,  [constargument(), registerargument()])

basic_commands = [mov, pld, pst, st, ld, add, sub, mul, div, jmp, in_, out, jne, jeq, jle, jlt, jge, jgt, inc, dec, ldi, sjmp]
