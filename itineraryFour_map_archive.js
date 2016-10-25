	// MJ MORGAN Itinerary (NO PATH)
	$(document).ready(function(){


		jQuery( '#infowindow' ).hide();

		function initialize() {

			var styles = [
			{
				stylers: [ 
				{ hue: "#ff0091" },
				{ saturation: -100 }
				]
			},{
				featureType: "road", 
				elementType: "geometry",
				stylers: [
				{ lightness: 100 },
				{ visibility: "simplified" }
				]
			},
			{
				featureType: "water", 
				elementType: "geometry",
				stylers: [
				{ color: "#000000" },
			// { lightness: 250 },
			{ visibility: "simplified" }
			]
		},

		{
			featureType: "road",
			elementType: "labels",
			stylers: [
         //Turns off road labels. 
         { visibility: "off" }
         ]
     }
     ];

     var map_options = {
     	center: new google.maps.LatLng(38.646774, -90.262974),
     	mapTypeId: google.maps.MapTypeId.TERRAIN,
     	zoom: 13,
     	panControl: false,
     	zoomControl: true,
     	scaleControl: true,
     	streetViewControl: false,
     	styles: styles,
     	mapTypeControl: true,
     	mapTypeControlOptions: {
     		mapTypeIds: [google.maps.MapTypeId.SATELLITE,google.maps.MapTypeId.TERRAIN],
     		style: google.maps.MapTypeControlStyle.DEFAULT,
     		position: google.maps.ControlPosition.TOP_RIGHT
     	}
     };

     map = new google.maps.Map(document.getElementById("mapCanvas"), map_options);

     map.setMapTypeId(google.maps.MapTypeId.TERRAIN);

     var image = {
     	url: 'image/home1.png',
     };

     var markers = [
	    // Detailed information for each marker, where it is located and where it lineks to
	    
	    ['St. Patrick Center', 38.633392, -90.195587, 'http://www.stpatrickcenter.org/'],
	    ['St. Peter & Paul Shelter', 38.607220, -90.203520, 'http://www.stspeterandpaulchurch-stlouis.net/Home/Christian-Service/Homeless-Shelter'],
	    ['Covenant House', 38.669753, -90.257100, 'http://covenanthousemo.org/'],
	    ['Gateway 180', 38.637589, -90.204696, 'http://www.gateway180.org/'],
	    ['New Life Evangelistic Center', 38.631705, -90.200557, 'http://www.newlifeevangelisticcenter.org/'],
	    ['Sunshine Ministries', 31.561392, -91.399077, 'http://www.sunshineministries.org/']
	    ];


// INFO WINDOW
var bounds = new google.maps.LatLngBounds();
var infoWindow = new google.maps.InfoWindow();
var gmarkers = [];
var marker, i;

for (i = 0; i < markers.length; i++) {
	marker = new google.maps.Marker({
		position: new google.maps.LatLng(markers[i][1], markers[i][2]),
		map: map,
		icon: image,
		title: [0],
		url:markers[i][3]
	     		// zIndex: markers[i][3],
	     	});
	bounds.extend(marker.getPosition());


//Infobox appear and disappear ///////////////////// 



google.maps.event.addListener(marker, 'mouseover', (function (marker, i) {
	return function () {  
		jQuery( '#infowindow' ).show();
		jQuery( '#infowindow' ).empty();
		jQuery( '#infowindow' ).append( content[i][0] );					
	}
})(marker, i));
gmarkers.push(marker);

google.maps.event.addListener(marker, 'click', function() {
	window.location.href = this.url;
});

google.maps.event.addListener(marker, 'mouseout', (function (marker, i) {
	return function () {  
		jQuery( '#infowindow' ).hide();					
	}
})(marker, i));
gmarkers.push(marker);

};
var mc = new MarkerClusterer(map, gmarkers, mcOptions);
map.fitBounds(bounds);
};
google.maps.event.addDomListener(window, 'load', initialize);
});



