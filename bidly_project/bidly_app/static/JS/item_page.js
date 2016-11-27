item_id = "";
currentBid = 0;
increment = 0;

//use item_id in proceeding ajax requests
$(document).ready(function() {
	var idParam = getURLParameter("item_id");
	item_id = idParam;
	currentBid = Number($("#current_bid").html());
	increment = Number($("increment").html());

	window.setInterval(updateCurrentBid,2000); //currently updates current bid every 2 seconds.

	$("#bid_button").click(makeBid);

});

function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

//update top bid
function getCurrentBid(){
	console.log("getting current bid");
	$.ajax({
		method: "GET",
		url: "/top_bid",
		data: {"item_id" : item_id},
		dataType: "json",
		success: updateCurrentBid,
		error: handleCurrentBidError
	});
};

function updateCurrentBid(data){
	if (data.status == 200) {
		var newBid = data.currentBid;
		$("#current_bid").html(newBid);
		currentBid = newBid;
	}
	else{
		console.log("Status Code not 200");
	}
}

function handleCurrentBidError(error){
	console.log(JSON.stringify(error));
}

function makeBid(){
	var bid = Number($("#bid_input").val());
	console.log(bid);

	if (bid < currentBid + increment) {
		console.log("Bid is too small");
		return; //Should add notification to front end
	}

	$.ajax({
		method: "POST",
		url: "/make_bid",
		data: {"item_id" : item_id, "bid" : bid},
		dataType: "json",
		success: bidSuccess,
		error: bidError
	});
};

function bidSuccess(data){
	if (data.status == 200) {
		//Update currentBid if successful
		var newBid = data.currentBid;
		$("#current_bid").html(newBid);
		currentBid = newBid;
		//Also give notification that their bid was successful
	}
	else{
		console.log("Status Code not 200");
	}
}

function bidError(error){
	console.log(JSON.stringify(error));
}