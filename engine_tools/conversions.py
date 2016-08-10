#!/usr/bin/python3

"""
A collection of conversion functions/generators.

"""

import math

def int_to_bytes(int_, width = None):
	"""
	.. _int_to_bytes:

	Converts the ``int`` ``int_`` to a ``bytes`` object.
	``len(result) == width``.

	If ``width`` is None, a number of bytes that is able to hold the
	number is choosen, depending on ``int_.bit_length()``.

	See also: bytes_to_int_
	"""
	if(width == None):
		width = int_.bit_length()
	byts = math.ceil(width / 8)
	return bytes([ (int_ >> (shift * 8)) & 0xff for shift in range(byts)])

def bytes_to_int(bytes_, width = None):
	"""
	.. _bytes_to_int:

	Converts the ``bytes`` object ``bytes_`` to an ``int``.
	If ``width`` is none, ``width = len(byte_) * 8`` is choosen.

	See also: int_to_bytes_

	*Example*

	>>> from py_register_machine2.engine_tools.conversions import *
	>>> i = 4012
	>>> int_to_bytes(i)
	b'\xac\x0f'
	>>> bytes_to_int(int_to_bytes(i)) == i
	True

	"""
	if(width == None):
		width = len(bytes_)
	else:
		width = width // 8
	if(width > len(bytes_)):
		padding = b"\x00" * (width - len(bytes_))
		bytes_ = bytes_ + padding
	ints = [ (int_ << (shift * 8)) for shift, int_ in enumerate(bytes_[:width])]
	return sum(ints)
