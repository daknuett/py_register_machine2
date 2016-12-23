#!/usr/bin/python3

"""
**py_register_machine2.app.web.front**: PRM2 Webapplication Datamodel

Every session generates a new RMServer object.
The RMServer contains the complete register machine.

It is possible to generate custom register machines by providing the 
RMServer by a dict with specifications.
"""

from ...core.register import *
from ...core.memory import *
from ...core.processor import *
from ...core.device import *
from ...tools.assembler import assembler
from ...commands.basic_commands import basic_commands
from ...engine_tools.conversions import chunks
from io import StringIO


defaults = {\
	"width": 64,
	"flash_enable": True,
	"ram_enable": True,
	"flash_width": 64,
	"rom_width": 64,
	"ram_width": 64,
	"registers": [\
		Register("r0", 64),
		Register("r1", 64),
		Register("r2", 64),
		Register("r3", 64),
		Register("r4", 64),
		Register("r5", 64),
		Register("r6", 64),
		Register("r7", 64),
		Register("r8", 64)
	],
	"commands": basic_commands,
	"flash_size": 2000,
	"rom_size": 256,
	"ram_size": 512
}

values = [\
	"width",
	"commands",
	"flash_width",
	"rom_width",
	"ram_width",
	"registers",
	"flash_size",
	"rom_size",
	"flash_enable",
	"ram_enable",
	"ram_size"
]



class RMServer(object):
	def __init__(self, descriptor = {}):
		self.load_machine(descriptor)

	def load_machine(self, descriptor):
		"""
			Load a complete register machine.
			The descriptor is a map, unspecified values are loaded from the default values.
		"""
		def get_cfg(name):
			if(name in descriptor):
				return descriptor[name]
			else:
				return defaults[name]
		self.processor = Processor(width = get_cfg("width"))
		self.rom = ROM(get_cfg("rom_size"), get_cfg("rom_width"))
		self.processor.register_memory_device(self.rom)
		self.registers = []

		if(get_cfg("ram_enable")):
			self.ram = RAM(get_cfg("ram_size"), get_cfg("ram_width"))
			self.processor.register_memory_device(self.ram)
		else:
			self.ram = None

		if(get_cfg("flash_enable")):
			self.flash = Flash(get_cfg("flash_size"), get_cfg("flash_width"))
			self.processor.register_device(self.flash)
		else:
			self.flash = None

		for register in get_cfg("registers"):
			self.processor.add_register(register)
			self.registers.append(register)
		for command in get_cfg("commands"):
			self.processor.register_command(command)
		self.processor.setup_done()

	def get_register_contents(self):
		for r in self.registers:
			yield r.name, r.read()

	def assemble_rom_code(self, asm):
		"""
			assemble the given code and program the ROM
		"""
		stream = StringIO(asm)
		worker = assembler.Assembler(self.processor, stream)
		try:
			result = worker.assemble()
		except BaseException as e:
			return e, None
		self.rom.program(result)
		return None, result
	def assemble_flash_code(self, asm):
		"""
			assemble the given code and program the Flash
		"""
		stream = StringIO(asm)
		worker = assembler.Assembler(self.processor, stream)
		try:
			result = worker.assemble()
		except BaseException as e:
			return e, None
		self.flash.program(result)
		return None, result
	def run(self):
		"""
			run the code. Returns an exception on failure.
		"""
		try:
			self.processor.run()
		except BaseException as e:
			return e
		return None
	def run_cycle(self):
		"""
			run one cycle. Returns an exception on failure.
		"""
		try:
			self.processor.do_cycle()
		except BaseException as e:
			return e
		return None
	def reset(self):
		"""
			reset the processor
		"""
		self.processor.reset()

	def flush_devices(self):
		"""
			overwrite the complete memory with zeros	
		"""
		self.rom.program([0 for i in range(self.rom.size)])
		self.flash.program([0 for i in range(self.flash.size)])
		for i in range(self.ram.size):
			self.ram.write(i, 0)
	def _format_mem(self, mem, format_ = "nl"):
		res = ""
		if(format_ in ("block", "blck")):
			for chunk in chunks(mem):
				res += "\t".join([str(m) for m in chunk]) + "\n"
			return res
		return "\n".join([str(m) for m in mem]) + "\n"
	def get_rom(self, format_ = "nl"):
		"""
			return a string representations of the rom
		"""
		rom = [self.rom.read(i) for i in range(self.rom.size)]
		return self._format_mem(rom, format_)
	def get_ram(self, format_ = "nl"):
		"""
			return a string representations of the ram
		"""
		ram = [self.ram.read(i) for i in range(self.ram.size)]
		return self._format_mem(ram, format_)
	def get_flash(self, format_ = "nl"):
		"""
			return a string representations of the flash
		"""
		flash = [self.flash.read(i) for i in range(self.flash.size)]
		return self._format_mem(flash, format_)
	
		

