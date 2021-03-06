#!/usr/bin/env python
# -*- coding:utf-8 -*-
html='''
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
      #map_canvas { height: 100% }
      #map_title {
        position: absolute;
        top: 30px;
        left: 50px;
        font-size: 35px;
        font-family: sans-serif;
        text-shadow: 0.1em 0.1em 0.2em black;
        color: white;
      }
      #city_board {
        position: absolute;
        top: 45px;
        left: 350px;
        font-size: 20px;
        font-family: sans-serif;
        text-shadow: 0.1em 0.1em 0.2em black;
        color: white;
      }
      #msg {
        position: absolute;
        font-size: 30px;
        font-family: sans-serif;
        text-shadow: 0.1em 0.1em 0.2em black;
        color: #d0d0ff;
        top: 200px;
        width: 600px;
        text-align: center;
      }
      #lightbox {
        width: 600px;
        height: 480px;
        background-color: #ffffff;
        opacity: 0.8;
      }
    </style>
    <script type="text/javascript" 
      src="http://maps.googleapis.com/maps/api/js?key=AIzaSyC5AdIXriwJl1vhMcbm661l3b5EF8QuIZk&sensor=false">
    <script type="text/javascript">
      function getHTTPObject() {
        if (typeof XMLHttpRequest == "undefined")
          XMLHttpRequest = function () {
            try { return new ActiveXObject("Msxml2.XMLHTTP.6.0"); }
              catch (e) {}
            try { return new ActiveXObject("Msxml2.XMLHTTP.3.0"); }
              catch (e) {} 
            try { return new ActiveXObject("Msxml2.XMLHTTP"); }
              catch (e) {} 
            return false;
          }
        return new XMLHttpRequest();
      }
    </script>
    <script type="text/javascript">
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
    </script>
    <script type="text/javascript">
      // 地图控件实例
      var map;

      // 预订任务队列
      var bookings_queue = [];

      // 定时器
      var loadWaitInterval = 2*1000;
      var syncInterval = 5*1000; //ms
      var displayInterval = 200; //ms
      var colors = [];

      //var markersByMonth = [];
      //for (var i = 0; i < 12; ++i) {
      //  markersByMonth.push([]);
      //}

      function initialize() {
        /*
        var mapOptions = {
          center: new google.maps.LatLng(37.550,115.579), // JiZhou Municipal Government
          zoom: 5,
          mapTypeId: google.maps.MapTypeId.TERRAIN
        };
        */

        // 配置地图属性
        var mapOptions = {
          zoom: 5,
          center: new google.maps.LatLng(34.271,108.946),//西安//(37.550,115.579), // JiZhou Municipal Government
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          mapTypeControl: false,
          backgroundColor: 'white',
          zoomControl: true,
          streetViewControl: false,
          panControl: false,
          styles: [
            {
              stylers: [
                { visibility: "off" }
              ]
            },{
              featureType: "water",
              stylers: [
                { visibility: "on" },
                { lightness: -50 },
                { saturation: -100 }
              ]
            },{
              featureType: "administrative.province",
              elementType: "geometry",
              stylers: [
                { visibility: "on" }
              ]
            },{
              featureType: "administrative.country",
              elementType: "geometry",
              stylers: [
                { visibility: "on" }
              ]
            },{
              featureType: "water",
              elementType: "labels",
              stylers: [
                { visibility: "off" }
              ]
            }
          ]
        };

        // 初始化地图实例
        map = new google.maps.Map(document.getElementById("map_canvas"),
            mapOptions);

        // 标记地点
        /*
        var myKuxunLatLng = new google.maps.LatLng(39.960,116.323)
        var myKuxunMarker = new google.maps.Marker({
          position: myKuxunLatLng,
          title: "酷讯旅游在这里！"
        });
        myKuxunMarker.setMap(map);
        */

        // 初始化颜色列表
        fillColorArray();

        // 设置数据同步定时器
        setTimeout(syncTimer, loadWaitInterval);

        // 设置展示定时器
        setTimeout(displayTimer, loadWaitInterval);
      }

      function syncTimer() {
        // sync data
        updateBookingList(storeAsyncRespData, errorHandler);

        // set next sync timer
        setTimeout(syncTimer, syncInterval);
      }

      function displayTimer() {
        // 标记展示
        while (booking = bookings_queue.shift())
        {
          displayAOrder(booking['city_name'], booking['coords'], 2015, 5);
          //console.log("%s %s (%s,%s)", booking['city'], booking['city_name'], booking['coords'][0], booking['coords'][1]);
          break;
        }

        // WARNING: 任务积累异常处理 dump display 机制（兜底机制）（理论上不会发生）
        if (bookings_queue.length > 1000) {
          len_a = bookings_queue.length;
          for (var i = 0; i < 900; i++) {
            booking = bookings_queue.shift();
            //队列阻塞野蛮处理
            //displayAOrder(booking['city_name'], booking['coords'], 2015, 5);
          };
          len_b = bookings_queue.length;
          console.log("booking queue dump %d -> %d", len_a, len_b);
        }
        
        // 根据队列长度动态调成timeout的毫秒数
        dynamicDisplayInterval = displayInterval;
        if (bookings_queue.length > 100)
        {
          dynamicDisplayInterval = 5;
          console.log('[dynamic interval] 3. SET %dms (%d)', dynamicDisplayInterval, bookings_queue.length);
        }
        else if (bookings_queue.length > 50)
        {
          dynamicDisplayInterval = Math.floor(syncInterval/(bookings_queue.length+1));
          console.log('[dynamic interval] 2. CALC %dms (%d/%d)', dynamicDisplayInterval, syncInterval, bookings_queue.length);
        }
        else
        {
          console.log('[dynamic interval] 1. default %dms (%d)', dynamicDisplayInterval, bookings_queue.length);
        }

        setTimeout(displayTimer, dynamicDisplayInterval);
      }

      function storeAsyncRespData(data) {
        status = data['result'];
        if (status != 0) {
          return;
        }

        books_dict = data['data'];
        in_cnt = 0;

        outer_queue = [];
        for (var key in books_dict) {
          in_cnt++;
          value = books_dict[key];
          item = {
            'city': key,
            'city_name': value['city_name'],
            'coords': [
              value['latitude'],
              value['longitude']
              ],
            'number': value['number']
          }

          // 分解城市number到多条记录
          inner_queue = [];
          for (var i = 0; i < value['number']; i++) {
            inner_queue.push(item);
          };
          outer_queue = outer_queue.concat(inner_queue);

          //console.log('IN '+in_cnt.toString()+'-'+JSON.stringify(item));
        }

        // 对本次装载队列进行随机排序
        outer_queue = shuffle(outer_queue);
        bookings_queue = bookings_queue.concat(outer_queue);

        // console窗口输出
        //console.log('IN '+JSON.stringify(data));
        console.log('IN count '+in_cnt.toString()+' queue '+bookings_queue.length.toString());
      }

      function errorHandler(data) {
        status = data;
        console.log('booking info async request failed - status '+status);
      }

      function shuffle(array) {
        var currentIndex = array.length, temporaryValue, randomIndex ;

        // While there remain elements to shuffle...
        while (0 !== currentIndex) {

          // Pick a remaining element...
          randomIndex = Math.floor(Math.random() * currentIndex);
          currentIndex -= 1;

          // And swap it with the current element.
          temporaryValue = array[currentIndex];
          array[currentIndex] = array[randomIndex];
          array[randomIndex] = temporaryValue;
        }

        return array;
      }

      // ------------- 互动控制 -------------
      function start() {
        /*
        if (unlock && ! running) {
          document.getElementById("lightbox").style.display = "none";
          document.getElementById("msg").style.display = "none";
          running = true;
          nextMonth();
        }
        */
      }

      function stop() {
        /*
        document.getElementById("lightbox").style.display = "block";
        document.getElementById("msg").style.display = "block";
        running = false;
        */
      }

      // ------------- 动画展示 -------------

      function displayAOrder(city, coords, year, month) {
        document.getElementById('city_board').innerHTML = city;

        var location = new google.maps.LatLng(coords[0], coords[1]);

        var outer = new google.maps.Marker({
          position: location,
          clickable: false,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 0.5,
            fillColor: colors[0],
            strokeOpacity: 1.0,
            strokeColor: colors[0],
            strokeWeight: 1.0,
            scale: 0,
          },
          optimized: false,
          //zIndex: year,
          map: map
        });

        var inner = new google.maps.Marker({
          position: location,
          clickable: false,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 1.0,
            fillColor: colors[0],
            strokeWeight: 0,
            scale: 0
          },
          optimized: false,
          //zIndex: year
        });
        //inner.year = year;

        //markersByMonth[month - 1].push(inner);

        for (var i = 0; i <= 10; i++) {
          setTimeout(setScale(inner, outer, i / 10), i * 60);
        }
      }

      function setScale(inner, outer, scale) {
        return function() {
          if (scale == 1) {
            outer.setMap(null);
          } else {
            var icono = outer.get('icon');
            icono.strokeOpacity = Math.cos((Math.PI/2) * scale);
            icono.fillOpacity = icono.strokeOpacity * 0.5;
            icono.scale = Math.sin((Math.PI/2) * scale) * 15;
            outer.set('icon', icono);

            var iconi = inner.get('icon');
            var newScale = (icono.scale < 2.0 ? 0.0 : 2.0);
            if (iconi.scale != newScale) {
              iconi.scale = newScale;
              inner.set('icon', iconi);
              if (!inner.getMap()) inner.setMap(map);
            }
          }
        }
      }

      function fillColorArray() {
        var max = 198;
        for (var i = 0; i < 44; i++) {
          if (i < 11) { // red to yellow
            r = max;
            g = Math.floor(i * (max / 11));
            b = 0;
          } else if (i < 22) { // yellow to green
            r = Math.floor((22 - i) * (max / 11));
            g = max;
            b = 0;
          } else if (i < 33) { // green to cyan
            r = 0;
            g = max;
            b = Math.floor((i - 22) * (max / 11));
          } else { // cyan to blue
            r = 0;
            g = Math.floor((44 - i) * (max / 11));
            b = max;
          }
          colors[i] = 'rgb(' + r + ',' + g + ',' + b + ')';
        }
      }
    </script>

  </head>
  <body onload="initialize()">
    <div id="map_canvas" style="width:100%; height:100%"></div>
    <div id="map_title">酒店搜索实时展示</div>
    <div id="city_board">北京</div>
    <div id="lightbox" onmouseover="start()"></div>
    <div id="msg"></div>
    <!--
    <div id="footer"></div>
    -->
  </body>
</html>
'''
