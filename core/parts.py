#!/usr/bin/python3

"""
**py_register_machine2.core.parts**: Basic parts of the register machine

"""

from ..engine_tools.operations import bitsetxor


class BUS(object):
	"""
	.. _BUS:

	**The BUS object**

	A BUS object connects the Processor with one or more 
	Memory alike operating devices (WordDevice_).

	Before the BUS starts working, devices can be registered, the
	address spaces of the devices are organized incremental::

		d1 = WordDevice(4)
		d2 = WordDevice(5)
		d3 = WordDevice(19)

		b = BUS()
		addr1 = b.register_device(d1)
		addr2 = b.register_device(d2)
		addr3 = b.register_device(d3)

		print( (addr1, addr2, addr3))
		# (0, 4, 9)
	
	Once the BUS started working (a read/write operation has been used)
	BUS.register_device will raise a BUSSetupError.
	If the addresspace of the BUS is too small do hold a new device,
	BUS.register_device will raise a BUSSetupError.


	The number of read/write actions can be observed by accessing the variables
	``reads`` and ``writes``
	"""
	def __init__(self, width = 64, debug = 0):
		self.width = width
		self.max_addr = 2 ** width
		self.start_addresses = {}
		self.index = {}
		self.devices = []
		self.current_max_offset = 0
		self.debug = debug
		self._lock = False
		self.reads = 0
		self.writes = 0
		self.truncate = Integer(width = width)

	def register_device(self, word_device):
		"""
		.. _register_device:

		Register the WordDevice_ ``word_device`` in the bus
		returns the start address of the device.

		raises: BUSSetupError_, if the device cannot be registered.

		"""
		if(self._lock):
			raise BUSSetupError("BUS already locked.")
		size = word_device.size
		if(self.current_max_offset + size >= self.max_addr):
			raise BUSSetupError("Addresspace({}) would exceed width of BUS({})".format(self.current_max_offset+ size,
						self.width))
		self.start_addresses[word_device] = self.current_max_offset
		res = self.current_max_offset
		self.current_max_offset += size
		self.index[range(res, self.current_max_offset)] = word_device
		self.devices.append(word_device)
		return res

	def read_word(self, offset):
		"""
		.. _read_word:

		Read one word from a device.
		The offset is ``device_addr + device_offset``, e.g.::

			offset = 3 # third word of the device
			offset += addr2
			b.read_word(offset)
			# reads third word of d2.

		Truncates the value according to ``width``.

		May raise BUSError_, if the offset exceeds the address space.

		"""	
		self._lock = True
		if(offset >= self.current_max_offset):
			raise BUSError("Offset({}) exceeds address space of BUS({})".format(offset, self.current_max_offset)) 
		self.reads += 1
		for addresspace, device in self.index.items():
			if(offset in addresspace):
				if(self.debug > 5):
					print("BUS::read({}) | startaddress({})> {}".format(offset, self.start_addresses[device],
								device.read(offset - self.start_addresses[device])))
				self.truncate.setvalue( device.read(offset - self.start_addresses[device]))
				return self.truncate.getvalue()


	def write_word(self, offset, word):
		"""
		.. _write_word:

		Writes one word from a device,
		see read_word_.
		"""
		self._lock = True
		if(offset >= self.current_max_offset):
			raise BUSError("Offset({}) exceeds address space of BUS({})".format(offset, self.current_max_offset)) 
		self.writes += 1
		
		self.truncate.setvalue(word)
		for addresspace, device in self.index.items():
			if(offset in addresspace):
				device.write(offset - self.start_addresses[device], self.truncate.getvalue()) 
	def device_count(self):
		return len(self.start_addresses)

class Integer(object):
	"""
	.. _Integer:

	The register machine may have a special width.
	This is handled by the Integer objects.
	
	Automatically truncates the value to the defined width.

	Use setvalue_ and getvalue_ or setuvalue_ and getuvalue_ to access the value.

	Uses a bitset internally.
	"""
	def __init__(self, value = 0, width = 64):
		self.width = width
		self.mask = 2 ** width - 1
		self._value = 0
		self._sign = 0
		self.setvalue(value)

	def setvalue(self, value):
		"""
		.. _setvalue:

		Set the signed value of the Integer.
		"""
		self._value = abs(value)
		self._sign = 0
		if(value < 0):
			self._sign = 1

	def getvalue(self):
		"""
		.. _getvalue:

		Get the signed value of the Integer, truncate it and handle Overflows.
		"""
		bitset = [0] * self.width
		zero = [1] * self.width

		for shift in range(self.width):
			bitset[shift] = (self._value & (1 << shift)) >> shift
		sign = 0
		if((not bitset[-1]) and self._sign):
			bitset[-1] = 1
			sign = 1
		elif(bitset[-1]):
			bitset = bitsetxor(bitset, zero)
			sign = 1
		
		value = [ bitset[shift] << shift for shift in range(self.width - 1)]
		value = sum(value)
		if(sign):
			return -1 * value
		return value

	def setuvalue(self, value):
		"""
		.. _setuvalue:

		Set the unsigned value of the Integer.
		"""
		self._value = value
		self._sign = 0
	def getuvalue(self):
		"""
		.. _getuvalue:

		Get the unsigned value of the Integer, truncate it and handle Overflows.
		"""
		bitset = [0] * self.width
		zero = [1] * self.width
		for shift in range(self.width):
			bitset[shift] = (self._value & (1 << shift)) >> shift
		if(self._sign):
			bitset = bitsetxor(zero, bitset)

		value = [ bitset[shift] << shift for shift in range(self.width)]
		return sum(value)




class WordDevice(object):
	"""
	.. _WordDevice:

	Base Device for the register machine.
	The words have the width ``width`` and are stored in an
	Integer_ object.

	Values are accessed by read_ and write_
	"""
	def __init__(self, size, width = 64, mode = 0b11, debug = 0):
		self.size = size
		self.repr_ = [Integer(width = width) for i in range(size)]
		self.mode = mode
		self.debug = debug

	def read(self, offset):
		"""
		.. _read:

		Returns the value of the memory word at ``offset``.

		Might raise WriteOnlyError_, if the device is write-only.
		Might raise AddressError_, if the offset exceeds the size of the device.
		"""
		if(not self.mode & 0b01):
			raise WriteOnlyError("Device is Write-Only")
		if(offset >= self.size):
			raise AddressError("Offset({}) not in address space({})".format(offset, self.size))
		return self.repr_[offset].getvalue()

	def write(self, offset, value):
		"""
		.. _write:

		Writes the memory word at ``offset`` to ``value``.

		Might raise ReadOnlyError_, if the device is read-only.
		Might raise AddressError_, if the offset exceeds the size of the device.
		"""
		if(not self.mode & 0b10):
			raise ReadOnlyError("Device is Read-Only")
		if(offset >= self.size):
			raise AddressError("Offset({}) not in address space({})".format(offset, self.size))
		self.repr_[offset].setvalue(value)


class Register(object):
	"""
	.. _Register:

	Basically hold one value and permitt read/write operations.
	There may be several subclasses, like Input/Output Register.

	The name will be used by the assembler.
	"""

	def __init__(self, name, width = 64):
		self.repr_ = Integer(0, width = width)
		self.name = name
		self.width = width


	def read(self):
		"""
		Return the content of the Register,
		may execute a function
		"""
		return self.repr_.getvalue()
	def write(self, value):
		"""
		Set the content of the Register,
		may execute a function
		"""
		self.repr_.setvalue(value)

		
		

class BUSSetupError(Exception):
	"""
	.. _BUSSetupError:

	   raised by a BUS if the setup failed.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)

class BUSError(Exception):
	"""
	.. _BUSError:

	   raised by a BUS if an operation failed.
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)


class ReadOnlyError(Exception):
	"""
	.. _ReadOnlyError:

	   raised by a device if it is read-only
	"""

	def __init__(self, *args):
		Exception.__init__(self, *args)
class WriteOnlyError(Exception):
	"""
	.. _WriteOnlyError:

	   raised by a device if it is write-only
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)
class AddressError(Exception):
	"""
	.. _AddressError:

	   raised by a device if the requested offset exceeds the size of the device
	"""
	def __init__(self, *args):
		Exception.__init__(self, *args)
