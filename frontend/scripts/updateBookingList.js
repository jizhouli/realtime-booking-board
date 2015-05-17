call_count = 1
function updateBookingList(successHandler, errorHandler) {
	var xhr = getHTTPObject();
	if (xhr) {
		// weather info - provided by www.openweathermap.org
		xhr.open("GET", "http://api.openweathermap.org/data/2.5/weather?q=Beijing,cn", true)
		
		xhr.onreadystatechange = function() {
			if (xhr.readyState == 4) {
				status = xhr.status;
				if (status == 200) {
					data = JSON.parse(xhr.responseText);
					weather = data['weather'][0]['main'];

					var para = document.createElement("p");
					var txt = document.createTextNode(call_count + ' : ' + weather);
					para.appendChild(txt);
					document.getElementById("footer").appendChild(para);
					call_count += 1;

					successHandler && successHandler([call_count + ' : ' + weather]);				
				}
				else {
					errorHandler && errorHandler(status);
				}
			}
		};
		xhr.send(null);
	} else {
		errorHandler && errorHandler(status);
		alert("Your browser doesn\'t support XMLHttpxhr");
	}
}