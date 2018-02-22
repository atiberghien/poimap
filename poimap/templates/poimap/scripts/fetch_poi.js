{% load static %}

var allPOI = {}
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
    {% if custom_api_poi_list_url %}
        var baseUrl = "{% url custom_api_poi_list_url %}";
    {% else %}
        var baseUrl = "{% url 'api-poi-list' %}";
    {% endif %}

    if(pathPK){
        url = baseUrl+"?path_pk="+pathPK;
    } else {
        url = baseUrl+"?bbox="+bboxCoords.join(',');
        {% if poi_type_slugs %}
        url+= "&type__slug__in={{poi_type_slugs|join:','}}"
        {% endif %}
    }

    return $.getJSON(url).done(function(data){
        clearLayersAndControls();
        $.each(data.features, function(index, poi){
            var marker = L.geoJSON(poi, {
                onEachFeature: function (feature, layer) {
                    layer.setIcon(L.AwesomeMarkers.icon({
                        icon: poi.properties.type.icon,
                        prefix : 'fa',
                    }));
                    layer.bindPopup(feature.properties.marker_popup, {'className':'custom-poimap-popup' });
                    layer.on("click", function(){
                        $(document).trigger("poimap:marker-clicked", [feature, layer]);
                    })
                    allPOI[feature.id] = [feature, layer];
                    $(document).trigger("poimap:marker-added", [poi]);
                }
            })
            if(typedPOILayers.hasOwnProperty(poi.properties.type.label)){
                typedPOILayers[poi.properties.type.label].addLayer(marker)
            }
            else {
                typedPOILayers[poi.properties.type.label] = L.layerGroup([marker]).addTo(map)

            }
        });
        {% if POI_UNDER_CONTROL and not remove_control %}
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
