if (!$) {
    $ = django.jQuery;
}

var inline_map = null;
var inline_field = null;

$(window).on('map:init', function(e) {
    inline_map = e.originalEvent.detail.map;
    inline_map.on('map:loadfield', function (me) {
        if(inline_field == null){ //UGLY, can not work with seveval inline
            inline_field = me.field
        }
        // console.log(inline_field);
    });
});


$(document).ready(function(){
    $("#id_poiaddress_set-0-country").val("FR");
    var address = $("#id_poiaddress_set-0-address");
    var zipcode = $("#id_poiaddress_set-0-zipcode");
    var city = $("#id_poiaddress_set-0-city");

    var geoButton = $("<button type='button'>Geoloc</button>").click(function(){
        var country = $("#id_poiaddress_set-0-country option:selected");
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
                           var marker = L.marker([lat, lng]);
                           console.log(inline_field);
                           inline_field.store.save(marker);
                           inline_field.load();
                           inline_map.panTo(new L.LatLng(lat, lng));
                           inline_map.setZoom(17);
                       }
                   }
               }
           })
       }
    })
    $("#id_poiaddress_set-0-country").after(geoButton);
});
