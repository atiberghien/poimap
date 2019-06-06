function fetchDataSource(map, url, poiFactoryCallback){
    return $.getJSON(url).done(function(data){

        if(data.hasOwnProperty('num_pages')){
            poiFactoryCallback(data.features).addTo(map);
            for (let index = 2; index <= data.num_pages; index++) {
                $.ajax({
                    dataType: "json",
                    async: false,
                    url: url+"&page="+index,
                }).done(function(data){
                    poiFactoryCallback(data.results.features).addTo(map);
                });
            }
        } else {
            poiFactoryCallback(data.features).addTo(map);
        }
    });
}

function fetchPOI(map, url, options) {
    /*
    Options can be :
    - pathPk : to filter poi according a specific path instead of boundbox
    - poiTypeSlugs : to filter according specific POITypes
    - hideControl : to hide layer control
    */

    var options = options == undefined ? {} : options;
    var pathPk = options.hasOwnProperty('pathPk') ? options.pathPk : null;
    var poiTypeSlugs = options.hasOwnProperty('poiTypeSlugs') ? options.poiTypeSlugs : null;
    var hideControl = options.hasOwnProperty('hideControl') ? options.hideControl : null;

    var bboxCoords = resizeBbox([startPoint.getLatLng().lng,
                                 startPoint.getLatLng().lat,
                                 endPoint.getLatLng().lng,
                                 endPoint.getLatLng().lat],
                                 1.1);

    if(pathPk){
        url += "?path_pk="+pathPk;
    } else {
        url += "?bbox="+bboxCoords.join(',');
        if(poiTypeSlugs){
            url+= "&poi_type_slugs="+poiTypeSlugs
        }
    }
    
    return fetchDataSource(map, url, createPOIMarker).done(function(data){        
        $.each(typedPOILayers, function(index, layer){
            layer.addTo(map);
        });
        if(!hideControl) {
            if(len(typedPOILayers)){
                typedPOILayerControl = L.control.layers(null, typedPOILayers, {collapsed : false}).addTo(map);
            }
        }
        $(document).trigger("poimap:fetch-secondary-data", [map, bboxCoords]);
    });
}
