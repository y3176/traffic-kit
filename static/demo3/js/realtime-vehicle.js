/**
 * WGS84转GCJ02(高德坐标)
 * @param wgsLat WGS84纬度
 * @param wgsLng WGS84经度
 * @returns { lat: number, lng: number } GCJ02坐标对象
 */
function wgs84ToGcj02(wgsLat, wgsLng) {
    if (isLocationOutOfChina(wgsLat, wgsLng)) {
        return { lat: wgsLat, lng: wgsLng };
    }
    
    const PI = 3.14159265358979324;
    const a = 6378245.0;
    const ee = 0.00669342162296594323;
    
    let dLat = transformLat(wgsLng - 105.0, wgsLat - 35.0);
    let dLng = transformLon(wgsLng - 105.0, wgsLat - 35.0);
    
    const radLat = wgsLat / 180.0 * PI;
    let magic = Math.sin(radLat);
    magic = 1 - ee * magic * magic;
    const sqrtMagic = Math.sqrt(magic);
    
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * PI);
    
    return { 
        lat: wgsLat + dLat,
        lng: wgsLng + dLng
    };
}

// 辅助函数
function transformLat(x, y) {
    let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
    ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0;
    return ret;
}

function transformLon(x, y) {
    let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
    ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(x * Math.PI)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0;
    return ret;
}

function isLocationOutOfChina(lat, lng) {
    return (lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271);
}


$(document).ready(function() {
    // 高德地图初始化
    var map = new AMap.Map('container', {
        zoom: 14,
        center: [112.96468906385225, 28.731705035721394], // 默认北京中心点
        viewMode: '2D'
    });
    
    // 车辆标记存储
    var vehicleMarkers = {};
    var lastRenderTime = 0;
    var frameCount = 0;
    var lastFpsUpdate = Date.now();

    
    // 更新FPS显示
    function updateFPS() {
        frameCount++;
        var now = Date.now();
        if (now - lastFpsUpdate >= 1000) {
            $('#fps').text(frameCount);
            frameCount = 0;
            lastFpsUpdate = now;
        }
    }
    
    // 创建车辆标记
    function createVehicleMarker(vehicle) {
        var p = wgs84ToGcj02(vehicle.lat,vehicle.lng)
        var marker = new AMap.Marker({
            position: new AMap.LngLat(p.lng, p.lat),
            content: createMarkerContent(vehicle),
            offset: new AMap.Pixel(-10, -10),
            extData: vehicle
        });
        
        // 点击标记显示信息窗口
        marker.on('click', function(e) {
            var infoWindow = new AMap.InfoWindow({
                content: `<div>
                    <h4>车辆信息</h4>
                    <p>ID: ${vehicle.id}</p>
                    <p>速度: ${vehicle.speed || 0} km/h</p>
                    <p>方向: ${vehicle.heading || 0}°</p>
                </div>`,
                offset: new AMap.Pixel(0, -30)
            });
            infoWindow.open(map, marker.getPosition());
        });
        
        return marker;
    }
    
    // 创建标记内容
    function createMarkerContent(vehicle) {
        var color = getColorBySpeed(vehicle.speed || 0);
        var angle = vehicle.heading || 0;
        
        var div = document.createElement('div');
        div.style.width = '20px';
        div.style.height = '20px';
        div.style.background = color;
        div.style.borderRadius = '50%';
        div.style.border = '2px solid white';
        div.style.transform = `rotate(${angle}deg)`;
        div.style.boxShadow = '0 0 5px rgba(0,0,0,0.5)';
        
        return div;
    }
    
    // 根据速度获取颜色
    function getColorBySpeed(speed) {
        if (speed < 20) return '#4CAF50'; // 绿色
        if (speed < 60) return '#FFC107'; // 黄色
        return '#F44336'; // 红色
    }
    
    // 更新车辆位置
    function updateVehiclePositions(vehicles) {
        var now = Date.now();
        $('#latency').text(now - vehicles.timestamp);
        
        // 更新车辆总数显示
        $('#vehicle-count').text(vehicles.data.length);
        
        // 批量更新标记位置
        var markersToAdd = [];
        
        $.each(vehicles.data, function(i, vehicle) {
            if (vehicleMarkers[vehicle.id]) {
                // 更新现有标记
                var p = wgs84ToGcj02(vehicle.lat,vehicle.lng)
                vehicleMarkers[vehicle.id].setPosition([p.lng, p.lat]);
                vehicleMarkers[vehicle.id].setContent(createMarkerContent(vehicle));
                vehicleMarkers[vehicle.id].getExtData().speed = vehicle.speed;
                vehicleMarkers[vehicle.id].getExtData().heading = vehicle.heading;
            } else {
                // 创建新标记
                var marker = createVehicleMarker(vehicle);
                vehicleMarkers[vehicle.id] = marker;
                markersToAdd.push(marker);
            }
        });
        
        // 添加新标记到地图
        map.add(markersToAdd);

        
        // 性能优化: 限制渲染频率
        if (now - lastRenderTime > 100) {
            updateFPS();
            lastRenderTime = now;
        }
    }
    
    // WebSocket连接
    function connectWebSocket() {
        // 获取当前主机名和端口号
        const host = window.location.hostname; // 当前主机名（IP 或域名）
        const port = window.location.port ? `:${window.location.port}` : ''; // 获取当前端口号，如果没有则为空

        // 如果你需要在生产环境中使用 HTTPS 和 ws:// 协议，处理不同协议：
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'; // 判断当前协议是 HTTPS 还是 HTTP，分别使用 wss:// 和 ws://

        // 构建 WebSocket URL
        const wsUrl = `${protocol}://${host}${port}/api/ws`;
        ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {
            console.log('WebSocket连接已建立');
        };
        
        ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            updateVehiclePositions(data);
        };
        
        ws.onclose = function() {
            console.log('WebSocket连接已关闭，5秒后尝试重连...');
            setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket错误:', error);
            ws.close();
        };
    }
    
    // 控制按钮事件
    $('#start-sumo').click(function() {
        fetch('/api/start-sumo', {  
            method: 'POST',  
            headers: {  
                'Content-Type': 'application/json'  
            },  
            body: JSON.stringify({})  
        })
        .then(response => response.json()) 
        .then(data => { alert(data) }) 
    });
    
    $('#stop-sumo').click(function() {
        fetch('/api/stop-sumo', {  
            method: 'POST',  
            headers: {  
                'Content-Type': 'application/json'  
            },  
            body: JSON.stringify({})  
        }) 
        .then(response => response.json()) 
        .then(data => { alert(data) }) 
    });
    
    // 初始化WebSocket连接
    connectWebSocket();
});
