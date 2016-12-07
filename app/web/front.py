#!/usr/bin/python3

import cherrypy, os
from .model import RMServer


static_path = os.path.abspath(os.path.dirname(__file__)) + "/static"
html_path = os.path.abspath(os.path.dirname(__file__)) + "/html"

conf = {\
	"/": {\
		'tools.sessions.on': True
	},
	"/static": {\
		'tools.staticdir.on': True,
     		'tools.staticdir.dir': static_path
	}
}

class Front(object):
	def __init__(self):
		pass
	@cherrypy.expose
	def index(self):
		html = open(html_path + "/RegisterMachine.pyhtml").read()
		return html.format(*["" for i in range(8)])
	
	@cherrypy.expose
	def assemble_rom_code(self, code = "ldi 0b1 ECR"):
		self.__load_rm_unless_loaded()
		exc, mc = cherrypy.session["rms"].assemble_rom_code(code)
		if(exc == None):
			return cherrypy.session["rms"]._format_mem(mc)
		cherrypy.session["lastexc"] = exc
		raise cherrypy.HTTPRedirect("/error")
	@cherrypy.expose
	def error(self):
		return str(cherrypy.session["lastexc"])


	def __load_rm_unless_loaded(self):
		if("rms" not in cherrypy.session):
			self.__load_default_rm()
	def __load_default_rm(self):
		cherrypy.session["rms"] = RMServer()
	def __set_rm(self, descriptor):
		cherrypy.session["rms"] = RMServer(descriptor)
		


if __name__ == "__main__":
	cherrypy.quickstart(Front(), "/", conf)
