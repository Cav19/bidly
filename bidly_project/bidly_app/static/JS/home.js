$(document).ready(function(){
  $('.carousel').slick({
    infinite: true,
    mobileFirst: true,
    swipe: true,
    touchMove: true,
    slidesToShow: 3,
    centerPadding: '60px',
    arrows: true,
  });

  getItemBids();

  $(".item").click(function(){
  	window.location.href = "/item_page/?item_id=" + this.id;
  });
});

 function getItemBids(){
	var items = document.getElementsByClassName("item");
	// TODO: Update this for loop to not get each of the items more than once if they're displayed more than once on the page. 
	for(i = 0; i < items.length; i++){
		$.ajax({
			method: 'GET',
			url: '/get_top_bid',
			data: {'item_id' : items[i].id}, // TODO: Update this so we don't require an id on each HTML element as well as a class. 
			dataType: 'json',
			success: updateTopBid, 
			error: handleError
		});
	}
}

var updateTopBid = function(data){
	if(data.current_bid != null){
		for(i = 0; i < $("." + data.item_id).length; i++){
			$("." + data.item_id)[i].children[1].children[2].innerHTML = "Current Bid: $" + data.current_bid;
		}
	}
	else{
		for(i = 0; i < $("." + data.item_id).length; i++){
			$("." + data.item_id)[i].children[1].children[2].innerHTML = "Current Bid: $" + data.current_bid;
		}
	}
};

var handleError = function(error){
	console.log(JSON.stringify(error));
};