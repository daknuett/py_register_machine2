
function put_rom_code(html)
{
	document.getElementById('ram').value = html;
}

function load_rom_code ()
{
	var asm = $("#assembly").val();
	$.ajax({type: "POST",
			url: "/assemble_rom_code",
			data: {code: asm}}).done(put_rom_code);
}
