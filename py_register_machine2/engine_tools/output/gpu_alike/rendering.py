from ....core import parts
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

class RenderDevice(parts.WordDevice):
	def __init__(self, renderer, width = 64, debug = 0):
		parts.WordDevice.__init__(self, 10,  width = width, mode = 0b11, debug = debug)
		self.renderer = renderer
	def write(self, offset, value):
		if(offset >= self.size):
			raise AddressError("Offset({}) not in address space({})".format(offset, self.size))
		self.repr_[offset].setvalue(value)
		if(offset == 9):
			self.renderer.interrupt()
	def clear_IR(self):
		self.repr_[9].setvalue(0)


class Renderer(object):
	"""
	.. _Renderer:

	Used to emulate a GPU.

	Basic Usage
	-----------

	The Renderer is accessed using a ``py_register_machine2.core.parts.WordDevice``.
	It consists of 10 memory blocks with different usages:

	Data Format Register *DFR* (offset 0)
		This Block defines the data format. For now
		only text mode is implemented (DFR = 0x01).
	Data Register *DR0 - DR7* (offset 1 - 8)
		Used to pass information to the Renderer
	Interrupt Register *IR* (offset 9)
		If the bit 0b01 is set in this register the Renderer will read the
		DFR and the Data Registers and process the information.
		The register is always zero'd after one render opearation.
		There might be other uses of this register in future
		(like a *clear-screen* bit).

	
	"""
	def __init__(self, output_device, height = 400, width = 400):
		self.device = RenderDevice(self)
		self.height = height
		self.width = width
		self.output_device = output_device

		self.max_chars_per_line = width // 6
		self.max_chars_per_col = height // 9

		self.char_buffer = [[(" ", 0xff, 0xff, 0xff) for i in range(self.max_chars_per_line)] for j in range(self.max_chars_per_col)]
		self.cursor = [0, 0]

		self.screen = Image.new("RGB", (height, width))
		self.drawer = ImageDraw.Draw(self.screen)

	def get_device(self):
		"""
		Returns the WordDevice_ used by the Renderer.
		"""
		return self.device
	def interrupt(self):
		"""
		Invoked on a write operation into the IR of the RendererDevice.
		"""
		if(self.device.read(9) & 0x01):
			self.handle_request()
		self.device.clear_IR()
	def handle_request(self):
		req_type = self.device.read(0)
		if(req_type == 0x01): 
			# text mode
			char = self.device.read(1)
			r, g, b = self.device.read(2), self.device.read(3), self.device.read(4)
			self.put_char(char, r, g, b)



	def put_char(self, char, r, g, b):
		"""
		Puts the character ``char`` into the char_buffer.
		Special characters:
			
		"\n"
			cursor[0] += 1
			cursor[1] = 0
		"\r"
			cursor[1] = 0
		"\t"
			cursor[1] += 8
		0
			equals " "
		"""
		r, g, b = r & 0xff, g & 0xff, b & 0xff
		if(char == 0):
			char = " "

		if(char == "\r"):
			self.cursor[1] = 0
			return
		if(char == "\t"):
			for i in range(8):
				self.put_char(" ", r, g, b)
			return
		
		if(self.max_chars_per_col > self.cursor[0]):
			if(char == "\n"):
				self.cursor[1] = 0
				self.cursor[0] += 1
				return

			if(self.max_chars_per_line > self.cursor[1]):
				self.char_buffer[self.cursor[0]][self.cursor[1]] = (char, r, g, b)
				self.cursor[1] += 1
			else:
				self.cursor[0] += 1
				self.cursor[1] = 0
				self.char_buffer[self.cursor[0]][self.cursor[1]] = (char, r, g, b)
				self.cursor[1] += 1
			self.draw_char_screen()
		else:
			self.char_buffer.append([(" ", 0xff, 0xff, 0xff) for i in range(self.max_chars_per_line)])
			self.cursor[0] -= 1
			self.put_char(char, r, g, b)

	def draw_char_screen(self):
		"""
		Draws the output buffered in the char_buffer.
		"""
		self.screen = Image.new("RGB", (self.height, self.width))
		self.drawer = ImageDraw.Draw(self.screen)

		for sy, line in enumerate(self.char_buffer):
			for sx, tinfo in enumerate(line):
				self.drawer.text((sx * 6, sy * 9), tinfo[0], fill=tinfo[1:])
		self.output_device.interrupt()



