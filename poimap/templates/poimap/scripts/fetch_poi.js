{% load static %}

var typedPOILayers = {}
var typedPOILayerControl = null
var secondaryPathLayers = null;
var secondaryPathLayerControl = null

function clearLayersAndControls(){
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

function fetchPOI(pathPK) {
    var bboxCoords = resizeBbox([startPoint.getLatLng().lng,
                                 startPoint.getLatLng().lat,
                                 endPoint.getLatLng().lng,
                                 endPoint.getLatLng().lat],
                                 1.1);
    if(pathPK){
        url = "{% url 'api-poi-list' %}?path_pk="+pathPK;
    } else {
        url = "{% url 'api-poi-list' %}?bbox="+bboxCoords.join(',');
    }

    return $.getJSON(url).done(function(data){

        clearLayersAndControls();
        var count = 0
        $.each(data.features, function(index, poi){
            var marker = L.geoJSON(poi, {
                onEachFeature: function (feature, layer) {
                    layer.setIcon(L.AwesomeMarkers.icon({
                        icon: poi.properties.type.icon,
                        prefix : 'fa',
                    }));
                    layer.bindPopup(feature.properties.marker_popup, {'className':'custom-poimap-popup' });
                    count++;
                    layer.on("click", function(){
                        $(document).trigger("poimap:marker-clicked", [feature, layer]);
                    })
                }
            })
            if(typedPOILayers.hasOwnProperty(poi.properties.type.label)){
                typedPOILayers[poi.properties.type.label].addLayer(marker)
            }
            else {
                typedPOILayers[poi.properties.type.label] = L.layerGroup([marker])
            }
        });
        {% if POI_UNDER_CONTROL %}
        if(len(typedPOILayers)){
            typedPOILayerControl = L.control.layers(null, typedPOILayers, {collapsed : false}).addTo(map);
        }
        {% else %}
            $.each(typedPOILayers, function(index, layer){
                layer.addTo(map);
            });
        {% endif %}
        $(document).trigger("poimap:fetch-secondary-data", [bboxCoords]);
    });
}
