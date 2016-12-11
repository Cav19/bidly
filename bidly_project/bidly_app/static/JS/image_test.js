$(document).ready(function(){
	$.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
});

function previewFile() {
  var preview = document.querySelector('img');
  var file    = document.querySelector('input[type=file]').files[0];
  var reader  = new FileReader();

  reader.addEventListener("load", function () {
    preview.src = reader.result;
    console.log(reader.result);
    $.ajax({
    	method: "POST",
    	data: {"image_url": reader.result},
    	url: "/image_test/",
    	dataType: "json",
    	success: handleSuccess,
    	error: handleError
    });
  }, false);

  if (file) {
    reader.readAsDataURL(file);
    console.log(reader.result)
  }
}

function handleSuccess(data){
	alert("success");
}

function handleError(error){
	alert(JSON.stringify(error));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}