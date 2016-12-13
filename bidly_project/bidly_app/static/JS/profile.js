$(document).ready(function(){
	var password;
	onLoad();

	var winChevronPosition = "left";
	var loseChevronPosition = "left";
	var fileText = "";

	$.ajaxSetup({
	    headers: { "X-CSRFToken": getCookie("csrftoken") }    
	});

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
	});

	$(".item").click(function(){
  		window.location.href = "/item_page/?item_id=" + this.id;
	});

	$("#save-auction").click(function(){
		readCSV();
	});

	$("#file").change(function(){
    	readURL(this);
	});

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
};


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
};

var updateTopBid = function(data){
	if(data.current_bid != null){
		$("#" + data.item_id).children().children()[2].innerHTML = "Current Bid: $" + data.current_bid;
	}
	else{
		$("#" + data.item_id).children().children()[2].innerHTML = "Current Bid: $0";
	}
};

function readURL(input) {
	// Source: http://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        console.log(input.files[0]);
        console.log(input.files[0].name);
        console.log(input.files[0].webkitRelativePath);
        reader.readAsText(input.files[0]);

        reader.onload = function (e) {
            fileText = e.target.result;
        }
    }
}

function readCSV(){
	var rows = fileText.split("\r\n");
	var headers = rows[0].split("\t");
	var allItems = [];
	for(i = 1; i < rows.length; i++){
		row = rows[i].split("\t");
		if(row[0] === ""){	// Not sure why but I was getting a row with a singular empty element at the end. Can look into it later but this works for now. 
			break;
		}
		item = {};
		for(j = 0; j < row.length; j++){
			// //find the image hosted on the local machine
			// if (headers[j].toString() == "image_url") {
			// 	var reader = new FileReader();
			// 	var imgPath = row[j].toString();
			// 	console.log(imgPath);
			// 	var imgFile = new File([""], imgPath);
			// 	reader.readAsDataURL(imgFile);
			// 	item[headers[j].toString()] = reader.result;
			// }
			item[headers[j].toString()] = row[j].toString();
		}
		console.log(item);

		allItems.push(item);
	}
	parse_img_files(allItems,0);
}

var parse_img_files = function(items,itemIndex){
	if (itemIndex == items.length) {
		create_auction(items);
		return;
	}
	var reader = new FileReader();
	item = items[itemIndex];
	var imgName = item["image_url"];
	var imgFile = imgFilesMap[imgName];
	reader.addEventListener("loadend", function(){
		item["image_url"] = reader.result;
		parse_img_files(items,itemIndex+1);
	});
	reader.readAsDataURL(imgFile);
}

var imgFilesMap = {};
function uploadImages(){
	var files  = $("#imgUpload")[0].files;
	for (var i = 0; i < files.length; i++) {
		var file = files[i];
		imgFilesMap[file.name] = file;
	}
	console.log(imgFilesMap);
}

$("#upload-images").click(function(){
	$("#imgUpload").click();
})

var create_auction = function(items){
	console.log(JSON.stringify(items));
	var data = {"url" : "/test/", "start_time" : "", "end_time" : "", "items" : items};
	data["items"] = JSON.stringify(data["items"]);
	$.ajax({
		method: 'POST',
		url: '/create_auction/',
		data: data,
		dataType: 'json',
		success: auctionCreated,
		error: handleError
	});
}

var auctionCreated = function(data){
	console.log("Auction created!");
}

function getCookie(name) {    
	var cookieValue = null;    
	if (document.cookie && document.cookie !== '') {        
		var cookies = document.cookie.split(';');        
		for (var i = 0; i < cookies.length; i++) {            
			var cookie = jQuery.trim(cookies[i]);            // Does this cookie string begin with the name we want?            
			if (cookie.substring(0, name.length + 1) === (name + '=')) {                
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));                
				break;            
			}        
		}    
	}    
	return cookieValue;
}