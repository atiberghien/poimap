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

var typedPOILayers = {}
var typedPOILayerControl = null
var secondaryPathLayers = null;
var secondaryPathLayerControl = null

function clearLayersAndControls(map){
    if(len(typedPOILayers)){
        for (var key in typedPOILayers) {
            typedPOILayers[key].removeFrom(map);
        }
        typedPOILayers = {};
    }
    if(typedPOILayerControl) {
        typedPOILayerControl.remove();
        typedPOILayerControl = null;
    }
    if(secondaryPathLayerControl){
        for (var key in secondaryPathLayers) {
            secondaryPathLayers[key].removeFrom(map);
        }
        secondaryPathLayers = null;
        secondaryPathLayerControl.remove();
        secondaryPathLayerControl = null;
    }
    $(".leaflet-control-layers").remove()
}

function fetchArea(map, url){
    return $.getJSON(url).done(function(area){
        rect = L.geoJSON(area)
        rect.setStyle({
            fill : false,
            color : 'grey'
        })
        startPoint = L.marker(rect.getBounds().getNorthWest());
        endPoint = L.marker(rect.getBounds().getSouthEast());
        map.fitBounds(rect.getBounds());
        $(document).trigger("poimap:fetch-data", [area]);
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

function computePath(map, currentPath){
    console.log("toto", startPoint, endPoint);
    var sliced = turf.lineSlice(startPoint.toGeoJSON(), endPoint.toGeoJSON(), fullPath.toGeoJSON().features[0]);

    if(currentPath) {
        map.removeLayer(currentPath)
    }
    var tempPath = L.geoJSON(sliced, { color : 'red'}).addTo(map);
    map.fitBounds(tempPath.getBounds());

    var length = turf.length(sliced);
    $("#distance").text(length.toFixed(2));

    fetchPOI(map);
    $(document).trigger("poimap:update-elevation-chart", [sliced.geometry.coordinates])

    return tempPath
}
