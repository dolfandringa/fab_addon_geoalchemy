$(document).ready({
  $('div.leaflet_map').each({
    var id = $(this).attr('id');
    L.map(id);
  });
});
