function len(obj) {
    var size = 0;
    for (let key in obj) {
        if (obj.hasOwnProperty(key)) {
            size++;
        }
    }
    return size;
};

function resizeBbox (bbox, factor) {
    var currentXDistance = (bbox[2] - bbox[0]);
    var currentYDistance = (bbox[3] - bbox[1]);
    var newXDistance = currentXDistance * factor;
    var newYDistance = currentYDistance * factor;
    var xChange = newXDistance - currentXDistance;
    var yChange = newYDistance - currentYDistance;

    var lowX = bbox[0] - (xChange / 2);
    var lowY = bbox[1] - (yChange / 2);
    var highX = (xChange / 2) + bbox[2];
    var highY = (yChange / 2) + bbox[3];

    var sized = [lowX, lowY, highX, highY];
    return sized;
}

L.Marker.prototype.fetchGeoInfo = function(labelId) {
    $.ajax({
        dataType: "json",
        url: "https://maps.googleapis.com/maps/api/geocode/json",
        data: {
            latlng : this.getLatLng().lat+","+this.getLatLng().lng,
            language : 'fr',
            location_type : 'GEOMETRIC_CENTER',
            key : "AIzaSyAThNRSpWOhnA2EGSeshFqLolrTPQx1hjo"
        },
        success: function(data){
            if(data.status == "OK"){
                if(data.results.length > 0) {
                    var poiResult = data.results[0];
                    $(labelId+" span.geo-text").text(poiResult.formatted_address);
                    $(labelId+" input").val(JSON.stringify(poiResult.geometry.location));
                }
            }
        }
    });
}

L.Marker.prototype.applyDragEventListener = function (currentPath, markerOptions) {
    this.on('drag', function(e) {
        var nearest = leafletKnn(currentPath).nearest(e.target.getLatLng(),1)[0];
        this.setLatLng([nearest.lat, nearest.lon]);
    });
    this.on('dragend', function(e) {
        this.fetchGeoInfo(markerOptions.labelId)
    });
}

function createPOIMarker(poi) {
    return marker = L.geoJSON(poi, {
        onEachFeature: function (feature, layer) {
            layer.setIcon(L.AwesomeMarkers.icon({
                icon: feature.properties.type.icon,
                prefix : 'fa',
            }));
            layer.bindPopup(feature.properties.marker_popup, {'className':'custom-poimap-popup' });
            layer.on("click", function(){
                $(document).trigger("poimap:marker-clicked", [feature, layer]);
            })
            allPOI[feature.id] = [feature, layer];
            $(document).trigger("poimap:marker-added", [feature]);
        }
    })
}




// var checkpoints = [];
// function updateCheckPoints(steps, stepLength) {
//     for (var i = 0; i < checkpoints.length; i++) {
//         map.removeLayer(checkpoints[i])
//     }
//     checkpoints = []
//     var geop = path.toGeoJSON().features[0]
//     for (var i = 1; i <= steps-1; i++) {
//         var along = turf.along(geop, stepLength * i, 'kilometers');
//         L.geoJSON(along, {
//             pointToLayer: function (feature, latlng) {
//                 var checkpoint = L.circleMarker(latlng, {
//                     radius : 2,
//                     color : 'red',
//                     fill : "red"
//                 });
//                 checkpoints.push(checkpoint);
//                 return checkpoint
//             }
//         }).addTo(map);
//     }
// }

// $("#kmPerDay").on("change", function(){
//     var geop = path.toGeoJSON().features[0]
//     var length = turf.lineDistance(geop, 'kilometers');
//
//     var stepLength = parseFloat($(this).val());
//     var steps = Math.round(length / stepLength);
//
//     updateCheckPoints(steps, stepLength);
// });
// $("#kmPerDay").change()
