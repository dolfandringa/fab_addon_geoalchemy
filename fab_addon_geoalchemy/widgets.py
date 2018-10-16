from wtforms.widgets import Input
from markupsafe import Markup
import logging
from copy import deepcopy
from geoalchemy2.shape import to_shape

log = logging.getLogger(__name__)


class LatLonWidget(Input):

    _ro_template = Markup(
        '<label>Latitude:</label> {latitude} '
        '<label>Longitude:</label> {longitude} '
        '<div class="leaflet_map" id="{fieldname}_map"></div>'
        '<script type="text/javascript">createROPointMap("{fieldname}_map", '
        '{latitude}, {longitude});</script>')

    @classmethod
    def getROMap(cls, value, fieldname):
        geom = to_shape(value)
        latitude = geom.y
        longitude = geom.x
        return cls._ro_template.format(latitude=latitude, longitude=longitude,
                                       fieldname=fieldname)

    def __call__(self, field, **kwargs):
        log.debug("Instantiating LatLonWidget")
        lonname = "{}_lon".format(field.name)
        latname = "{}_lat".format(field.name)
        kwargs.setdefault("id", field.id)
        lonkwargs = deepcopy(kwargs)
        latkwargs = deepcopy(kwargs)
        lonkwargs["id"] = lonname
        latkwargs["id"] = latname
        log.debug("Field.data: {}".format(field.data))
        log.debug("kwargs: {}".format(kwargs))
        if "value" not in kwargs:
            if isinstance(field.data, str):
                lon = field.lon
                lat = field.lat
            elif isinstance(field.data, dict) \
                    and lonname in field.data and latname in field.data:
                lon = field.data[lonname]
                lat = field.data[latname]
            else:
                lon = None
                lat = None
            if lon is not None:
                lonkwargs["value"] = lon
            if lat is not None:
                latkwargs["value"] = lat
        if "required" not in kwargs and "required" in getattr(field,
                                                              "flags", []):
            kwargs["required"] = True
        log.debug("Widget kwargs: {}".format(kwargs))
        lat = Markup('Latitude: <input type="text" %s>' %
                     self.html_params(name="%s_lat" % field.name, **latkwargs))
        lon = Markup(' Longitude: <input type="text" %s>' %
                     self.html_params(name="%s_lon" % field.name, **lonkwargs))
        leaflet_map = Markup('<div class="leaflet_map" %s></div>' %
                             self.html_params(id='%s_map' % field.name))
        script = Markup('<script type="text/javascript">' +
                        'createPointMap("{id}_map","{id}_lat", "{id}_lon")'
                        .format(id=field.name) +
                        ';</script>')
        return lat+lon+leaflet_map+script
