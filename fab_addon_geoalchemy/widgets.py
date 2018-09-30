from wtforms.widgets import Input
from flask import render_template
from markupsafe import Markup
import logging
from copy import deepcopy

log = logging.getLogger(__name__)


class LatLonWidget(Input):

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
        return lat+lon+leaflet_map
