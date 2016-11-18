$(document).ready(function(){
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
});

