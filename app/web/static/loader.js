
/* remove the error window */
function action_prologue()
{
	document.getElementById('errsect').style.display = "none";
}

/* display errors in the error section */
function __display_error(html )
{
	document.getElementById('errcode').value = html;
}
function display_error()
{

	$.ajax({url: "/error"}).done(__display_error);
	document.getElementById('errsect').style.display = "";
	$.ajax({url: "/clearerr"});
}

/* write the ROM mc representation */
function put_rom_code(html)
{
	if(html == "error")
	{
		display_error();
	}
	else
	{
		document.getElementById('romcode').value = html;
	}
}

/* get the ROM assembly, assemble it and refresh the view */
function load_rom_code ()
{
	action_prologue();
	var asm = $("#assemblyr").val();
	$.ajax({type: "POST",
			url: "/assemble_rom_code",
			data: {code: asm}}).done(put_rom_code);
	refresh_rom_content();
}
function put_flash_code(html)
{
	if(html == "error")
	{
		display_error();
	}
	else
	{
		document.getElementById('flashcode').value = html;
	}
}
function put_ram_code(html)
{
	document.getElementById('ramcode').value = html;
}

function load_flash_code ()
{
	action_prologue();
	var asm = $("#assemblyf").val();
	$.ajax({type: "POST",
			url: "/assemble_flash_code",
			data: {code: asm}}).done(put_flash_code);
	refresh_flash_content();
}


function run_cycle()
{
	action_prologue();
	// FIXME: add a way to load the RAM, ROM and Flash view section here!
	$.ajax({url: "/run_cycle"}).done(check_for_errors);
	// FIXME: add registers and stuff
	refresh_memory_views();
}
function run()
{
	action_prologue();
	// FIXME: add a way to load the RAM, ROM and Flash view section here!
	$.ajax({url: "/run"}).done(check_for_errors);
	// FIXME: add registers and stuff
	refresh_memory_views();
}


function check_for_errors(result)
{
	if(result == "error")
	{
		display_error();
	}
}

/*
 Refresh all memory views...
 */

function refresh_memory_views()
{
	refresh_ram_content();
	refresh_rom_content();
	refresh_flash_content();
	refresh_register_content();
}

function refresh_register_content()
{
	$.ajax({url: "/registers"}).done(function( html ){document.getElementById("registeroutput").innerHTML = html;});
}
function refresh_ram_content()
{
	$.ajax({url: "/ram"}).done(put_ram_code);
}
function refresh_rom_content()
{
	$.ajax({url: "/rom"}).done(put_rom_code);
}
function refresh_flash_content()
{
	$.ajax({url: "/flash"}).done(put_flash_code);
}

function reset()
{
	action_prologue();
	$.ajax({url: "/reset"});
	refresh_memory_views();
}
function flush()
{
	action_prologue();
	$.ajax({url: "/flush"});
	refresh_memory_views();
}
