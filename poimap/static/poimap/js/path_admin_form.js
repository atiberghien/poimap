if (!$) {
    $ = django.jQuery;
}

var map = null;
var field = null;

$(window).on('map:init', function(e) {
    map = e.originalEvent.detail.map;
    map.on('map:loadfield', function (me) {
        field = me.field
    });
});


$(document).ready(function(){
    var geoField = "<div class='form-row field-gpx'><div><label for='id_gpx'>Importer un gpx:</label></div><input id='id_gpx' type='file' class='btn btn-primary' name='gpx'/></div>"
    $(".field-geom").after(geoField);

    $("#id_gpx").on('change', function(){
        file = $(this)[0].files[0];
        var fr = new FileReader();
        fr.onload = function(event) {
            var raw = (new DOMParser()).parseFromString(event.target.result, 'text/xml');
            var path = L.geoJSON(toGeoJSON.gpx(raw))
            field.store.save(path);
            field.load();
        };
        fr.readAsText(file);
    });

});
