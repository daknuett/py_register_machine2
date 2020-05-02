import http.server, io
from .rendering import Renderer

DEFAULT_HTML ='''\
<html><head><meta http-equiv="refresh" content="2"</head><body>
	<h>GPU rendered Output</h>
	<p><img src="/image"></p>
</body></html>''' 

class HTTPOutput(http.server.BaseHTTPRequestHandler):
	"""
	A HTTP Request Handler used to dislplay the rendered PNG images.
	"""
	def do_HEAD(self):
		self.send_response(200)
		if(self.path == "image"):
			self.send_header("Content-type", "image/png")
		else:
			self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		self.send_response(200)
		if(self.path == "/image"):
			self.send_image()
		else:
			self.send_root()

	def send_root(self):
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(self.server.html.encode("UTF-8"))
#		self.wfile.close()
	def send_image(self):
		self.send_header("Content-type", "image/png")
		self.end_headers()
		self.wfile.write(self.server.image.getvalue())
#		self.wfile.close()


class HTTPOutputServer(http.server.HTTPServer):
	"""
	HTTP server used to display GPU alike rendered images.
	"""
	def __init__(self, html = DEFAULT_HTML, addr = ('localhost', 8080)):
		http.server.HTTPServer.__init__(self, addr, HTTPOutput)
		self.html = html
		self.renderer = Renderer(self)
		self.image = io.BytesIO()
	def interrupt(self):
		"""
		Invoked by the renderering.Renderer, if the image has changed.
		"""
		self.image = io.BytesIO()
		self.renderer.screen.save(self.image, "png")
	def get_renderer(self):
		return self.renderer

