function fetchPOI(map, pathPK) {
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
        clearLayersAndControls(map);
        $.each(data.features, function(index, poi){
            var marker = createPOIMarker(poi);
            if(typedPOILayers.hasOwnProperty(poi.properties.type.label)){
                typedPOILayers[poi.properties.type.label].addLayer(marker)
            }
            else {
                typedPOILayers[poi.properties.type.label] = L.layerGroup([marker]).addTo(map)

            }
        });
        {% if not remove_control %}
        if(len(typedPOILayers)){
            typedPOILayerControl = L.control.layers(null, typedPOILayers, {collapsed : false}).addTo(map);
        }
        {% else %}
            $.each(typedPOILayers, function(index, layer){
                layer.addTo(map);
            });
        {% endif %}
        $(document).trigger("poimap:fetch-secondary-data", [map, bboxCoords]);
    });
}
