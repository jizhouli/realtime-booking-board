

call_count = 1
function updateBookingList(successHandler, errorHandler) {
	TEST_MODE = true;
	
	if (TEST_MODE == true) {
		//readTextFile(successHandler, errorHandler);
		dumbUpdateBookingList(successHandler, errorHandler);
		return;
	}
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
					var txt = document.createTextNode(call_count + '-' + weather);
					para.appendChild(txt);
					document.getElementById("footer").appendChild(para);
					
					successHandler && successHandler([call_count + '-' + weather]);

					call_count += 1;
				}
				else {
					errorHandler && errorHandler(status);
					console.warn("get status error - " + status.toString())
				}
			}
		};
		xhr.send(null);
	} else {
		errorHandler && errorHandler(status);
		console.warn("Your browser doesn\'t support XMLHttpxhr");
	}
}

function readTextFile(successHandler, errorHandler)
{
    var rawFile = getHTTPObject();
    rawFile.open("GET", 'sample_response.json', true);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                successHandler && successHandler(allText);
            }
        }
    }
    rawFile.send(null);
}

function dumbUpdateBookingList(successHandler, errorHandler)
{
	allText={"data":{"beijing":{"city_name":"北京","latitude":"29.6521816254","number":6,"longitude":"91.1243438721"},"dalian":{"city_name":"大连","latitude":"39.9489974976","number":10,"longitude":"116.812675476"},"chengdu":{"city_name":"成都","latitude":"30.6050014496","number":3,"longitude":"105.256065369"},"foshan":{"city_name":"佛山","latitude":"23.1147823334","number":2,"longitude":"113.867370605"},"songjiang":{"city_name":"松江","latitude":"31.01354","number":2,"longitude":"121.248047"},"xian":{"city_name":"西安","latitude":"32.6095314026","number":2,"longitude":"110.788101196"},"zhangjiajie":{"city_name":"张家界","latitude":"28.29646492","number":1,"longitude":"109.731285095"},"nanjing":{"city_name":"南京","latitude":"40.1468925476","number":1,"longitude":"116.657989502"},"lijiang":{"city_name":"丽江","latitude":"27.2835998535","number":1,"longitude":"100.857650757"},"tongxin":{"city_name":"同心","latitude":"36.985607","number":1,"longitude":"105.91803"},"jianshui":{"city_name":"建水","latitude":"23.622095","number":1,"longitude":"102.83287"},"changsha":{"city_name":"长沙","latitude":"27.8705978394","number":1,"longitude":"112.917045593"},"zhengzhou":{"city_name":"郑州","latitude":"34.753742218","number":3,"longitude":"113.683189392"},"mudanjiang":{"city_name":"牡丹江","latitude":"29.8291873932","number":4,"longitude":"91.4930343628"},"yueyang":{"city_name":"岳阳","latitude":"20.0220718384","number":1,"longitude":"110.330802917"},"tianjin":{"city_name":"天津","latitude":"39.8268737793","number":9,"longitude":"119.513206482"},"shanghai":{"city_name":"上海","latitude":"31.2097110748","number":2,"longitude":"121.563171387"},"hongyuan":{"city_name":"红原","latitude":"32.7975196838","number":1,"longitude":"102.551620483"},"baise":{"city_name":"百色","latitude":"38.2650489807","number":1,"longitude":"140.87588501"},"dongying":{"city_name":"东营","latitude":"37.4361610413","number":1,"longitude":"118.669799805"},"chongqing":{"city_name":"重庆","latitude":"29.5037662575","number":1,"longitude":"29.5037662575"},"shenzhen":{"city_name":"深圳","latitude":"22.65074","number":4,"longitude":"113.825554"},"shantou":{"city_name":"汕头","latitude":"35.7153587341","number":1,"longitude":"139.79725647"},"yichang":{"city_name":"宜昌","latitude":"30.205317","number":3,"longitude":"110.679878"},"yantai":{"city_name":"烟台","latitude":"36.869102478","number":1,"longitude":"120.527992249"},"taizhou1":{"city_name":"泰州","latitude":"32.920552","number":2,"longitude":"119.838659"},"guangzhou":{"city_name":"广州","latitude":"23.141351","number":2,"longitude":"113.349924"},"haerbin":{"city_name":"哈尔滨","latitude":"45.7528114319","number":3,"longitude":"126.666381836"},"quanzhou":{"city_name":"泉州","latitude":"35.6990699768","number":1,"longitude":"139.697280884"},"wuhan":{"city_name":"武汉","latitude":"30.5066146851","number":1,"longitude":"30.5066146851"},"kunming":{"city_name":"昆明","latitude":"24.759563","number":9,"longitude":"103.280792"},"bangbu":{"city_name":"蚌埠","latitude":"39.9299850464","number":2,"longitude":"116.395645142"},"fushun":{"city_name":"抚顺","latitude":"42.1188812256","number":1,"longitude":"124.924316406"},"chifeng":{"city_name":"赤峰","latitude":"43.2182388306","number":1,"longitude":"117.358566284"},"qingdao":{"city_name":"青岛","latitude":"31.2180423737","number":1,"longitude":"121.440391541"},"yishui":{"city_name":"沂水","latitude":"35.7764816284","number":1,"longitude":"118.642555237"},"cangzhou":{"city_name":"沧州","latitude":"38.2982254028","number":2,"longitude":"116.894142151"},"xiamen":{"city_name":"厦门","latitude":"24.4547364878","number":4,"longitude":"118.072450907"},"linan":{"city_name":"临安","latitude":"30.235119","number":1,"longitude":"119.722687"},"nanning":{"city_name":"南宁","latitude":"40.0211181641","number":1,"longitude":"116.435462952"},"chuxiong1":{"city_name":"楚雄","latitude":"39.8926811218","number":1,"longitude":"116.40045929"},"huangshan":{"city_name":"黄山","latitude":"40.1383743286","number":1,"longitude":"116.29058075"},"shijiazhuang":{"city_name":"石家庄","latitude":"38.050883","number":1,"longitude":"114.529817"},"lasa":{"city_name":"拉萨","latitude":"36.1244659424","number":1,"longitude":"110.698699951"},"hangzhou":{"city_name":"杭州","latitude":"30.5439052582","number":3,"longitude":"119.879966736"},"fuzhou":{"city_name":"福州","latitude":"26.271572113","number":1,"longitude":"117.64780426"},"changzhou":{"city_name":"常州","latitude":"40.2232894897","number":3,"longitude":"117.523216248"},"ningbo":{"city_name":"宁波","latitude":"29.6970043182","number":2,"longitude":"120.235824585"},"taiyuan":{"city_name":"太原","latitude":"38.9983978271","number":1,"longitude":"113.591156006"},"dongguan":{"city_name":"东莞","latitude":"23.039665","number":1,"longitude":"113.791245"}},"result":0};
	successHandler && successHandler(allText);
}
