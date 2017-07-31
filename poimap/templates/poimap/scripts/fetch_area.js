$.getJSON("{% url 'api-area' area_slug %}").done(function(area){
    var rect = L.geoJSON(area)
    rect.setStyle({
        fill : false,
        color : 'grey'
    })
    rect.addTo(map)
    startPoint = L.marker(rect.getBounds().getNorthWest());
    endPoint = L.marker(rect.getBounds().getSouthEast());
    map.fitBounds(rect.getBounds());
    $(document).trigger("poimap:fetch-data", [area]);
});
