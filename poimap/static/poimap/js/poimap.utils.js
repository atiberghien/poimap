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

function clearAll(map){
    for (let [id, poi] of Object.entries(allPOI)) {
        map.removeLayer(poi[1])   
    }
    allPOI = {};
    clearLayersAndControls();
    
}

function hideAll(map, poiList){
    let cpt = 0
    for(let [feature, marker] of poiList){
        if(map.hasLayer(marker)) {
            cpt++;
            map.removeLayer(marker);
        }
    }
    console.log(`Hide ${cpt} marker`);
}

function removeAll(map, poiList){
    let cpt = 0
    for(let [feature, marker] of poiList){
        if(map.hasLayer(marker) && allPOI.hasOwnProperty(feature.id)) {
            cpt++;
            map.removeLayer(marker);
            delete allPOI[feature.id];
        }
    }
    console.log(`Remove ${cpt} marker`);
}

function showAll(map, poiList){
    let cpt = 0
    for(let [feature, marker] of poiList){
        if(!map.hasLayer(marker)) {
            cpt++;
            marker.addTo(map);
        }
    }
    console.log(`Show ${cpt} marker`);
    
}

function getPOIByTypeSlugs(map, typeSlugs){
    let poiList = Object.values(allPOI).filter(function(poi){
        let [feature, marker] = poi;
        return typeSlugs.includes(feature.properties.type.slug); //&& map.getBounds().contains(marker.getLatLng());
    });
    console.log(`Select ${poiList.length} of ${typeSlugs}`);
    
    return poiList;
}

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
    return L.geoJSON(poi, {
        pointToLayer: function(geoJsonPoint, latlng) {
            
            var color = geoJsonPoint.properties.type.color ? geoJsonPoint.properties.type.color : 'blue';   
            var layer = L.marker(latlng, {draggable: false});
            if(geoJsonPoint.properties.type.icon_file_url){
                layer.setIcon(L.icon({
                    iconUrl: geoJsonPoint.properties.type.icon_file_url,
                    iconSize:  [28, 28],
                    popupAnchor:  [15, -50]
                }));
            } 
            else if(geoJsonPoint.properties.type.icon){
                layer.setIcon(L.BeautifyIcon.icon({
                    icon: geoJsonPoint.properties.type.icon,
                    iconShape: 'circle',
                    backgroundColor: color,
                    borderColor: color,
                    textColor: 'white'
                }));
            } else {
                layer.setIcon(L.BeautifyIcon.icon({
                    iconShape: 'doughnut',
                    borderWidth: 5,
                    borderColor: color
                }));
            }
            layer.bindPopup(geoJsonPoint.properties.marker_popup, {'className':'custom-poimap-popup' })
            return layer
        }, 
        onEachFeature: function (feature, layer) {
            var color = feature.properties.type.color ? feature.properties.type.color : 'black';
            if(typedPOILayers.hasOwnProperty(`<span style='color:${color}'>${feature.properties.type.label}</span>`)){
                typedPOILayers[`<span style='color:${color}'>${feature.properties.type.label}</span>`].addLayer(layer)
            }
            else {
                typedPOILayers[`<span style='color:${color}'>${feature.properties.type.label}</span>`] = L.layerGroup([layer])
            }

            layer.on("click", function(){
                $(document).trigger("poimap:marker-clicked", [feature, layer]);
            });
            allPOI[feature.id] = [feature, layer];
            $(document).trigger("poimap:marker-added", [feature]);
        }
    })
}

function computePath(map, fullPath, currentPath){
    if(!fullPath){
        return null;
    }
    var sliced = turf.lineSlice(startPoint.toGeoJSON(), endPoint.toGeoJSON(), fullPath.toGeoJSON().features[0]);

    if(currentPath) {
        map.removeLayer(currentPath)
    }
    var tempPath = L.geoJSON(sliced, { color : 'red'}).addTo(map);
    map.fitBounds(tempPath.getBounds());

    var length = turf.length(sliced);
    $("#distance").text(length.toFixed(2));

    $(document).trigger("poimap:update-elevation-chart", [sliced.geometry.coordinates])

    return tempPath
}
