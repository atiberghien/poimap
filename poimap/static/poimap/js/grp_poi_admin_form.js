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

    var row = $("<div class='form-row grp-row grp-cells-1 plop'>");
    var box = $("<div class='field-box l-2c-fluid l-d-4'>");
    var geoButton = $("<button type='button' class='grp-button default'>Géolocalisation à partir de l'adresse</button></div>");

    $("#id_country").parents("fieldset.address").append(row);
    row.append(box)
    box.append(geoButton);

    geoButton.click(function(){
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
                           console.log(field);
                           console.log(field.store);
                           field.load();
                       }
                   }
               }
           })
       }
    })

});
