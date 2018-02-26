var rect = null //the area

var startPoint = null;
var endPoint = null;

var startIcon = L.AwesomeMarkers.icon({
    icon: 'flag',
    prefix : 'fa',
    markerColor: 'green'
});
var endIcon = L.AwesomeMarkers.icon({
    icon: 'flag',
    prefix : 'fa',
    markerColor: 'red'
});

var startPointOptions = {
    draggable: false,
    // draggable: true,
    icon : startIcon,
    // labelId : "#start-"+path_.properties.slug
}

var endPointOptions = {
    draggable: false,
    // draggable: true,
    icon :endIcon,
    // labelId : "#end-"+path_.properties.slug
}

var allPOI = {}
