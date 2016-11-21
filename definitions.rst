PyRegisterMachine2 Definitions
******************************

Citation
========

If you want to cite PyRegisterMachine2 or a part of its documentation
you should always use the following format:

::
	PyRegisterMachine2[<implementation>][<branch>][<version>]
	<author(s)> 
	<interpreter>

Where author should refer at least to the authors that contributed
50 % of the design of your version (followed by a ``et al.`` if there are more authors).
The interpreter is a list of the coders of at 50 % of the code (followed by a ``et al.`` if there are more interpreter).

An example for the current implementation::

	PyRegisterMachine2[py3-std][master][0.0.5]
	Daniel Knüttel
	Daniel Knüttel

Register Machine Definitions
============================

One might define his own machine. This is *always* done by defining a function
(or a static method, if the language does not provide functions).
This function must return a 4-tuple::

	(processor, rom, ram, flash)

There are two types of definitions:

- **Final Definitions** must not be changed after instantiation, that includes, that ``Processor.setup_done`` has already been called.
- **Extensible Definitions** might be changed after instantiation. ``Processor.setup_done`` must be called after instantiation.

Short Name Conventions
----------------------

- *Core Definitions* 

	are provided in the standard engine. They must not be final.
	A core definition is always in the package ``py_register_machine2.machines``.
	The name should provide a hint about what the result is, like
	``simple_machine`` or ``big_machine``.

- *Private Definitions* 
	
	are provided by a person / institution.
	They have to follow the following name convention::

		prm2-<version>-<name>-<width>-<defversion>
		prm2_<version>_<name>_<width>_<defversion>

	Note that ``-`` and ``_`` are treated equally and might be converted to each other, 
	for example to handle language specific problems.

	- ``version`` should be the used PyRegisterMachine2 version, a ``.`` might be replaced by a ``q`` (``.`` and ``q`` are treated equally).
	- ``name`` should identify the machine and might give a hint about the resulting engine. All characters in ``name`` must be in ``'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'``.
	- ``width`` must be smallest width of all parts of the register machine.
	- ``defversion`` should follow the rules of ``version`` and defines the version of the definition.




Long Name Definitions
---------------------


