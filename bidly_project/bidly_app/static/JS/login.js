$(document).ready(function(e){
	$(".phone_num").keydown(function(e){
		console.log("Keydown");
		var input = e.target || e.srcElement;
		var value = input.value;
		if (value.length == 3) {
			if (input.id != "last_num") {
				$(this).next('.phone_num').focus();
			}
		}
		if (value.length == 4) {
			$(this).next('.phone_num').focus();
		}
	});
});
