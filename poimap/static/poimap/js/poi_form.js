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

    $("#id_country").val("FR");
    var address = $("#id_address");
    var zipcode = $("#id_zipcode");
    var city = $("#id_city");

    var geoButton = $("<div class='field-box'><button type='button' class='default'>Géolocalisation à partir de l'adresse</button></div>").click(function(){
        var country = $("#id_country option:selected");
        if(country.val() && zipcode.val() && address.val()){
            var addr = (address.val()+",+"+zipcode.val()+"+"+city.val()).replace(" ","+")
            $.ajax({
               dataType: "json",
               url: "https://maps.googleapis.com/maps/api/geocode/json",
               data: {
                   address : addr,
                   key : "AIzaSyAThNRSpWOhnA2EGSeshFqLolrTPQx1hjo"
               },
               success: function(data){
                   if(data.status == "OK"){
                       if(data.results.length > 0) {
                           var cityResult = data.results[0]
                           var lat = cityResult.geometry.location.lat;
                           var lng = cityResult.geometry.location.lng;
                           var marker = L.marker([lat, lng])
                           field.store.save(marker);
                           field.load();
                           map.panTo(new L.LatLng(lat, lng));
                           map.setZoom(17);
                       }
                   }
               }
           })
       }
    })
    $(".form-row.field-zipcode.field-city.field-country").append(geoButton);

    $('#id_gpx').on('change', function(){
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
