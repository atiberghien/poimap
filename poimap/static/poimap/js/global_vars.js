var rect = null //the area

var fullPath = null;
var path = null;

var startPoint = null;
var endPoint = null;

var startIcon = L.BeautifyIcon.icon({
    icon: "flag",
    iconShape: 'circle',
    backgroundColor: 'green',
    borderColor: 'green',
    textColor: 'white'
});

var endIcon = L.BeautifyIcon.icon({
    icon: "flag",
    iconShape: 'circle',
    backgroundColor: 'red',
    borderColor: 'red',
    textColor: 'white'
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
