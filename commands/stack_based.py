#!/usr/bin/python3


"""
**py_register_machine2.commands.stack_based**: A bunch of stack based commands

+----------+--------+---------------------------------------------------+
| mnemonic | opcode | Description 					|
+==========+========+===================================================+
| push a   | 0x18   | *(SP--) = a                                       |
+----------+--------+---------------------------------------------------+
| pop a    | 0x19   | a = *(++SP)                                       |
+----------+--------+---------------------------------------------------+
| call a   | 0x1a   | *(SP--) = PC; PC += a                             |
+----------+--------+---------------------------------------------------+
| scall a  | 0x1b   | *(SP--) = PC; PC = a                              |
+----------+--------+---------------------------------------------------+
| ret      | 0x1c   | PC = *(++SP)                                      |
+----------+--------+---------------------------------------------------+

all stackbased commands are available in the list ``stack_based_commands``.
"""

from ..core.commands import *

def push_function(register_interface, memory_BUS, device_BUS, register):
	sp = register_interface.read(2)
	memory_BUS.write_word(sp, register_interface.read(register))
	sp -= 1
	register_interface.write(2, sp)

def pop_function(register_interface, memory_BUS, device_BUS, register):
	sp = register_interface.read(2)
	sp += 1
	register_interface.write(register, memory_BUS.read_word(sp))
	register_interface.write(2, sp)

def call_function(register_interface, memory_BUS, device_BUS, addr):
	pc = register_interface.read(0)
	sp = register_interface.read(2)
	memory_BUS.write_word(sp, pc)
	sp += 1
	register_interface.write(2, sp)
	addr -= 2
	pc += addr
	register_interface.write(0, pc)

def ret_function(register_interface, memory_BUS, device_BUS):
	sp = register_interface.read(2)
	sp += 1
	register_interface.write(0, memory_BUS.read_word(sp))
	register_interface.write(2, sp)

def scall_function(register_interface, memory_BUS, device_BUS, addr):
	pc = register_interface.read(0)
	sp = register_interface.read(2)
	memory_BUS.write_word(sp, pc)
	sp += 1
	register_interface.write(2, sp)
	addr -= 2
	pc = addr
	register_interface.write(0, pc)

push = FunctionCommand("push", 0x18, 1, push_function, [registerargument()])
pop = FunctionCommand("pop", 0x19, 1, pop_function, [registerargument()])
call = FunctionCommand("call", 0x1a, 1, call_function, [constargument()])
scall = FunctionCommand("scall", 0x1b, 1, scall_function, [constargument()])
ret = FunctionCommand("ret", 0x1c, 0, ret_function, [])

stack_based_commands = [push, pop, call, scall, ret]
