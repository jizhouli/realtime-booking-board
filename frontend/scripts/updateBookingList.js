call_count = 1
function updateBookingList() {
	var request = getHTTPObject();
	if (request) {
		// weather info - provided by www.openweathermap.org
		request.open("GET", "http://api.openweathermap.org/data/2.5/weather?q=Beijing,cn", true)
		
		request.onreadystatechange = function() {
			if (request.readyState == 4) {
				jsonObject = JSON.parse(request.responseText);
				weather = jsonObject['weather'][0]['main'];

				var para = document.createElement("p");
				var txt = document.createTextNode(call_count + ' : ' + weather);
				para.appendChild(txt);
				document.getElementById("footer").appendChild(para);
				call_count += 1;
			}
		};
		request.send(null);
	} else {
		alert("Your browser doesn\'t support XMLHttpRequest");
	}
}