#!/usr/bin/python3


"""
**py_register_machine2.commands.gym_bav_16**: Instruction set compatible to the register machine used in the bavarian gymnasium.

+----------+--------+---------------------------------------------------+
| mnemonic | opcode | Description 					|
+==========+========+===================================================+
| DLOAD c  | 0x01   | A = c  (c is a number)                            |
+----------+--------+---------------------------------------------------+
| LOAD r   | 0x02   | A = r (r is a register)                           |
+----------+--------+---------------------------------------------------+
| STORE r  | 0x03   | r = A                                             |
+----------+--------+---------------------------------------------------+
| ADD r    | 0x04   | A = A + r (r is a register)                       |
+----------+--------+---------------------------------------------------+
| SUB r    | 0x05   | A = A - r                              	        |
+----------+--------+---------------------------------------------------+
| MULT r   | 0x06   | A = A * r					        |
+----------+--------+---------------------------------------------------+
| DIV r    | 0x07   | A = A / r                              	        |
+----------+--------+---------------------------------------------------+
| JUMP c   | 0x08   | PC = c (c is a constant)                          |
+----------+--------+---------------------------------------------------+
| HALT     | 0x09   | ECR = 1 (halts the engine)                        |
+----------+--------+---------------------------------------------------+
| JNE c    | 0x0a   | if(A != 0): PC = c                                |
+----------+--------+---------------------------------------------------+
| JEQ c    | 0x0b   | if(A == 0): PC = c                     	        |
+----------+--------+---------------------------------------------------+
| JLT c    | 0x0c   | if(A < 0): PC = c                                 |
+----------+--------+---------------------------------------------------+
| JLE c    | 0x0d   | if(A <= 0): PC = c                     	        |
+----------+--------+---------------------------------------------------+
| JGT c    | 0x0f   | if(A > 0): PC = c                                 |
+----------+--------+---------------------------------------------------+
| JGE c    | 0x10   | if(A >= 0): PC = c                     	        |
+----------+--------+---------------------------------------------------+
"""

from ..core.commands import * 

def dload_function(register_interface, memory_BUS, device_BUS, c):
	register_interface.write("A", c)
def load_function(register_interface, memory_BUS, device_BUS, r):
	register_interface.write("A", register_interface.read(r))
def store_function(register_interface, memory_BUS, device_BUS, r):
	register_interface.write(r, register_interface.read("A"))

def arith_function(register_interface, memory_BUS, device_BUS, r, f):
	a = register_interface.read("A")
	r_ = register_interface.read(r)
	register_interface.write("A", f(a, r_))

def add_function(register_interface, memory_BUS, device_BUS, r):
	arith_function(register_interface, memory_BUS, device_BUS, r, lambda a,b: a + b)
def sub_function(register_interface, memory_BUS, device_BUS, r):
	arith_function(register_interface, memory_BUS, device_BUS, r, lambda a,b: a - b)
def mult_function(register_interface, memory_BUS, device_BUS, r):
	arith_function(register_interface, memory_BUS, device_BUS, r, lambda a,b: a * b)
def div_function(register_interface, memory_BUS, device_BUS, r):
	arith_function(register_interface, memory_BUS, device_BUS, r, lambda a,b: a // b)

def jump_function(register_interface, memory_BUS, device_BUS, c):
	register_interface.write("PC", c * 2)
def halt_function(register_interface, memory_BUS, device_BUS):
	register_interface.write("ECR", 1)

def branch_function(register_interface, memory_BUS, device_BUS, c, f):
	if(f(register_interface.read("A"))):
		register_interface.write("PC", c * 2)

DLOAD = FunctionCommand("DLOAD", 0x01, 1, dload_function, [constargument()])
LOAD = FunctionCommand("LOAD", 0x02, 1, load_function, [registerargument()])
STORE = FunctionCommand("STORE", 0x03, 1, store_function, [registerargument()]) 
ADD = FunctionCommand("ADD", 0x04, 1, add_function, [registerargument()])
SUB = FunctionCommand("SUB", 0x05, 1, sub_function, [registerargument()])
MULT = FunctionCommand("MULT", 0x06, 1, mult_function, [registerargument()])
DIV = FunctionCommand("DIV", 0x07, 1, div_function, [registerargument()])
JUMP = FunctionCommand("JUMP", 0x08, 1, jump_function, [constargument()])
HALT = FunctionCommand("HALT", 0x09, 0, halt_function, [ArgumentType(type_ = "const", can_default = True)])
JNE = FunctionCommand("JNE", 0x0a, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x != 0), [constargument()])

JEQ = FunctionCommand("JEQ", 0x0b, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x == 0), [constargument()])

JLT = FunctionCommand("JLT", 0x0c, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x < 0),  [constargument()])

JLE = FunctionCommand("JLE", 0x0d, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x <= 0),   [constargument()])

JGT = FunctionCommand("JGT", 0x0f, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x > 0),  [constargument()])

JGE = FunctionCommand("JGE", 0x10, 1, 
	lambda register_interface, memory_BUS, device_BUS, c:\
		branch_function( register_interface, memory_BUS, device_BUS, c, lambda x: x >= 0),  [constargument()])

commands = [DLOAD, LOAD, STORE, ADD, SUB, MULT, DIV, JUMP, HALT, JNE, JEQ, JLT, JLE, JGT, JGE]
