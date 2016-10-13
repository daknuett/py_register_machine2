#!/usr/bin/python3

"""
**py_register_machine2.core.interrupts**: Basic module to provide Interrupts.


"""


class Interrupt(object):
	"""
	.. _Interrupt:
	
	The Base Class for Interrupts. 
	If ``Interrupt.interrupt`` is invoked this will invoke ``Processor.interrupt`` and provide the address of the 
	Interrupt.

	This will allow one to place an ISR (Interrupt Service Routine) at this address.
	"""
	def __init__(self, address, name, processor):
		self.enable = False
		self.address = address
		self.processor = processor
		self.name = name
		self.processor.add_interrupt(self)
	def interrupt(self):
		"""
		Will interrupt the Processor, if the Interrupt is enabled.
		"""
		if(self.enable):
			self.processor.interrupt(self.address)


class Counter(Interrupt):
	"""
	.. _Counter:

	A Counter/Timer implementation.

	The ``__init__`` method will inject an ``on_cycle_callback`` into the Processor.
	This callback will increment the internal counter variable by one.
	If the internal counter reaches a predefined value the ``interrupt`` method will be invoked.


	"""

	def __init__(self, address, name, processor, overflow_size):
		Interrupt.__init__(self, address, processor)
		self.processor.on_cycle_callbacks.append(self.increment_counter)
		self.counter = 0
		self.overflow = overflow_size

	def increment_counter(self):
		self.counter += 1
		if(self.counter >= self.overflow):
			self.counter = 0
			self.interrupt()

class Autoreset(Interrupt):
	"""
	.. _Autoreset:

	A really rude form of the Watchdog.
	This Interrupt will force the Processor to jump to offset ``0``.
	"""

	def __init__(self, name, processor, overflow_size):
		Interrupt.__init__(self, 0, processor)
		self.counter = 0
		self.overflow = overflow_size
		self.processor.on_cycle_callbacks.append(self.increment_counter)
	def increment_counter(self):
		self.counter += 1
		if(self.counter >= self.overflow):
			self.counter = 0
			self.interrupt()
		
