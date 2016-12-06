$(document).ready(function(){
	var password;
	onLoad();

	var winChevronPosition = "left";
	var loseChevronPosition = "left"

	$("#win-chevron").click(function(){
		if(winChevronPosition === "left"){
			this.className = "glyphicon glyphicon-chevron-down";
			winChevronPosition = "down";
		}
		else if(winChevronPosition === "down"){
			this.className = "glyphicon glyphicon-chevron-left";
			winChevronPosition = "left";
		}
	});

	$("#lose-chevron").click(function(){
		if(loseChevronPosition === "left"){
			this.className = "glyphicon glyphicon-chevron-down";
			loseChevronPosition = "down";
		}
		else if(loseChevronPosition === "down"){
			this.className = "glyphicon glyphicon-chevron-left";
			loseChevronPosition = "left";
		}
	});

	$("#change-pw").click(function(){
		var popup = document.getElementById("pwpopup");
		popup.classList.toggle("show");
	});

	$("#save").click(function(){
		$.ajax({
			method: 'POST', 
			url: '/change_profile',
			data: {
				'email': document.getElementById("email").value,
				'phone_number': document.getElementById("phone_number").value,
				'username': document.getElementById("username").value,
				'userId' : 1 
			},
			dataType: 'json',
			success: saveSuccess,
			error: handleError
		});
	})
});

function onLoad(){
	$.ajax({
		method: 'GET',
		url: '/get_profile_info',
		data: {"userId" : 1},
		dataType: 'json',
		success: updateProfileInfo,
		error: handleError
	});
	getItemBids();
}

var updateProfileInfo = function(data){
	if(data.status == 200){
		document.getElementById("email").placeholder = data.email;
		document.getElementById("phone_number").placeholder = data.phone_number;
		document.getElementById("username").placeholder = data.username;
		password = data.password;
	}
	else{
		console.log("Error getting profile info.");
	}
};

var handleError = function(error){
	console.log(JSON.stringify(error));
};

var saveSuccess = function(data){
	if(data.status == 200){
		alert("Data saved successfully!");
	}
};

function getItemBids(){
	var items = document.getElementsByClassName("item container");
	for(i = 0; i < items.length; i++){
		$.ajax({
			method: 'GET',
			url: '/get_top_bid',
			data: {'item_id' : items[i].id},
			dataType: 'json',
			success: updateTopBid, 
			error: handleError
		});
	}
}

var updateTopBid = function(data){
	$("#" + data.item_id).children().children()[2].innerHTML = "Current Bid: $" + data.current_bid;
};