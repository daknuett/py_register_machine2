Installing PyRegisterMachine2
*****************************

PyRegisterMachine2 is a simple python3-package, so the only thing one has to do is to place the folder in the ``$PYTHONPATH``. One can get the ``$PYTHONPATH`` in the following ways::

	echo $PYTHONPATH
	python3 -c "import sys; print(sys.path)"

* Local Installation

Usually the local path is ``/home/<username>/.local/lib/python3.5/site-packages``, so you are able to install the package via git::

	cd /home/daniel/.local/lib/python3.5/site-packages
	git clone https://github.com/daknuett/py_register_machine2


* Global Installation::

	cd /usr/local/lib/python3.5/dist-packages
	git clone https://github.com/daknuett/py_register_machine2



