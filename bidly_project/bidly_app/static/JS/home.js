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
});

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
	if(data.current_bid != null){
		$("#" + data.item_id).children().children()[2].innerHTML = "Current Bid: $" + data.current_bid;
	}
	else{
		$("#" + data.item_id).children().children()[2].innerHTML = "Current Bid: $0";
	}
};

var handleError = function(error){
	console.log(JSON.stringify(error));
};