item_id = "";
currentBid = 0;
increment = 0;

//use item_id in proceeding ajax requests
$(document).ready(function() {
	var idParam = getURLParameter("item_id");
	item_id = idParam;
	currentBid = Number($("#current_bid").html());
	increment = Number($("#increment").html());

	window.setTimeout(getCurrentBid,2000); //currently updates current bid every 2 seconds.

	$("#bid_button").click(makeBid);

	$.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

});

function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

//update top bid
function getCurrentBid(){
	$.ajax({
		method: "GET",
		url: "/get_top_bid",
		data: {"item_id" : item_id},
		dataType: "json",
		success: updateCurrentBid,
		error: handleCurrentBidError
	});
};

var updateCurrentBid = function(data){
	if (data.status == 200) {
		var newBid = data.current_bid;
		$("#current_bid").html(newBid);
		currentBid = newBid;
	}
	else{
		console.log("Status Code not 200");
	}
	window.setTimeout(getCurrentBid,2000); //currently updates current bid every 2 seconds.
}

var handleCurrentBidError = function(error){
	console.log(JSON.stringify(error));
	window.setTimeout(getCurrentBid,2000); //currently updates current bid every 2 seconds.
}

function makeBid(){
	var bid = Number($("#bid_input").val());

	if (bid < (currentBid + increment)) {
		console.log("Bid is too small");
		return; //Should add notification to front end
	}

	$.ajax({
		method: "POST",
		url: "/make_bid/",
		data: {"item_id" : item_id, "bid" : bid, "user_id" : 1}, //TODO: How do we find user ID? Is that already handled with django authentication and the cookie?
		dataType: "json",
		success: bidSuccess,
		error: bidError
	});
};

var bidSuccess = function(data){
	if (data.status == 200) {
		//Update currentBid if successful
		var newBid = data.current_bid;
		$("#current_bid").html(newBid);
		currentBid = newBid;
		//Also give notification that their bid was successful
	}
	else{
		console.log("Status Code not 200");
	}
}

var bidError = function(error){
	console.log(JSON.stringify(error));
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