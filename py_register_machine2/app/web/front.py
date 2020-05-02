#!/usr/bin/python3

"""
**py_register_machine2.app.web.front**: Webapplication controller

Run 
::

	python3 -m py_register_machine2.app.web.front

to start the server.

This module uses py_register_machine2.app.web.model, cherrypy
and a bunch of HTML/CSS/JS to provide a webinterface.

All actions are performed by AJAX.
"""

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
		cherrypy.session["err"] = False
		exc, mc = cherrypy.session["rms"].assemble_rom_code(code)
		if(exc == None):
			return cherrypy.session["rms"]._format_mem(mc)
		else:
			cherrypy.session["err"] = True
		cherrypy.session["lastexc"] = exc
		return "error"
	@cherrypy.expose
	def assemble_flash_code(self, code = "ldi 0b1 ECR"):
		self.__load_rm_unless_loaded()
		cherrypy.session["err"] = False
		exc, mc = cherrypy.session["rms"].assemble_flash_code(code)
		if(exc == None):
			return cherrypy.session["rms"]._format_mem(mc)
		else:
			cherrypy.session["err"] = True
		cherrypy.session["lastexc"] = exc
		return "error"
	@cherrypy.expose
	def error(self):
		self.__load_rm_unless_loaded()
		return str(cherrypy.session["lastexc"])
	@cherrypy.expose
	def ram(self):
		self.__load_rm_unless_loaded()
		return cherrypy.session["rms"].get_ram()
	@cherrypy.expose
	def rom(self):
		self.__load_rm_unless_loaded()
		return cherrypy.session["rms"].get_rom()
	@cherrypy.expose
	def flash(self):
		self.__load_rm_unless_loaded()
		return cherrypy.session["rms"].get_flash()

	@cherrypy.expose
	def run(self):
		self.__load_rm_unless_loaded()
		e = cherrypy.session["rms"].run()
		if(e):
			cherrypy.session["lastexc"] = e
			return "error"
		return ""
	@cherrypy.expose
	def run_cycle(self):
		self.__load_rm_unless_loaded()
		e = cherrypy.session["rms"].run_cycle()
		if(e):
			cherrypy.session["lastexc"] = e
			return "error"
		return ""
	@cherrypy.expose
	def reset(self):
		self.__load_rm_unless_loaded()
		cherrypy.session["rms"].reset()
		return ""
	@cherrypy.expose
	def flush(self):
		self.__load_rm_unless_loaded()
		cherrypy.session["rms"].flush_devices()
		return ""
		
	@cherrypy.expose
	def clearerr(self):
		cherrypy.session["lastexc"] = None
	
	@cherrypy.expose
	def registers(self):
		s = "<table>"
		for regname, content in cherrypy.session["rms"].get_register_contents():
			s += '<tr><td id="{regname}_name">{regname}</td><td id="{regname}_content"><input type="number" class="regcont" id="{regname}_cont" value="{content}" /></td></tr>'.format(regname = regname, content = content)
		return s + "</table>"

	def __load_rm_unless_loaded(self):
		if("rms" not in cherrypy.session):
			self.__load_default_rm()
	def __load_default_rm(self):
		cherrypy.session["rms"] = RMServer()
	def __set_rm(self, descriptor):
		cherrypy.session["rms"] = RMServer(descriptor)
		


if __name__ == "__main__":
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0'
	})
	cherrypy.quickstart(Front(), "/", conf)
