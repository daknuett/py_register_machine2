#!/usr/bin/python3

"""
Operations used by the engine.
"""


def bitsetxor(b1, b2):
	"""
	If b1 and b2 would be ``int`` s this would be ``b1 ^ b2`` :

	>>> from py_register_machine2.engine_tools.operations import bitsetxor
	>>> b1 = [1, 1, 1, 1]
	>>> b2 = [1, 1, 0, 1]
	>>> bitsetxor(b1, b2)
	[0, 0, 1, 0]
	>>> bin(0b1111 ^ 0b1101)
	'0b10'
	"""
	res = []
	for bit1, bit2 in zip(b1, b2):
		res.append( bit1 ^ bit2)
	return res
