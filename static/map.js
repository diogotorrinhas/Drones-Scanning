var obuIcon = L.icon({
    iconUrl: "static/drone.png",
    iconSize: [18, 18],
    iconAnchor: [17, 37],
    popupAnchor: [8, -33]
});

var map = L.map('map').setView([40.63164591573186, -8.661021708857298], 16);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var markers = []; //array with the markers

function updateMarkers(obuPositions) {
    // Remove existing markers
    //markers.forEach(function (marker) {
    //   map.removeLayer(marker);
    //});
    markers.forEach(delMarker)

    let i = 0
    // Add new markers based on updated positions
    console.log("LENGTH DOS MAKERS ANTES DE OS METER NO MAPA: " + markers.length)

    for (var key in obuPositions) {
        console.log("key: " + key + " latitude: " + obuPositions[key]["latitude"] + " longitude: " + obuPositions[key]["longitude"])
        markers[i] = L.marker([obuPositions[key]["latitude"], obuPositions[key]["longitude"]], {icon: obuIcon}).addTo(map).bindTooltip(key, {permanent: false});
        i++;
        console.log("MARKERS: " + markers) //Markers added to the map
    }
    console.log("LENGTH DOS MAKERS DEPOISSS DE OS METER NO MAPA: " + markers.length)
    //console.log("MARKERS: " + markers) //Markers added to the map
}

function obuCall() {
    $.ajax({
        url: '',
        type: 'get',
        contentType: 'application/json',
        dataType: 'json',
        success: function (response) {
            updateMarkers(response);
        }
    });
}

function delMarker(value, index, array){
    map.removeLayer(value)
}

$(document).ready(function () {
    setInterval(obuCall, 1000);
});