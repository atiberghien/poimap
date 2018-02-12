$(document).ready(function(){
    $('input[type="range"]').rangeslider({
        polyfill : false,
        onInit: function() {
            $('label[for=id_step]').html(`Nombre de km/jour : `)
        },
        onSlide: function(position, value) {
            $('label[for=id_step]').html(`Nombre de km/jour : ${value}`)

        },
    });

    $("#id_start_point > option:first").attr("selected", "selected");
    $("#id_end_point > option:last").attr("selected", "selected");
    
    $("#id_start_point, #id_end_point").change(function(){
        var startPoiId = parseInt($("#id_start_point").val());
        var endPoiId = parseInt($("#id_end_point").val());
        $(document).trigger("poimap:itinerary-bounds-change", [startPoiId, endPoiId])
    });

})
