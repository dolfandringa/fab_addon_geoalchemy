from wtforms.fields import Field
from wtforms.utils import unset_value
from .widgets import LatLonWidget
import logging
from geoalchemy2.elements import WKBElement
from shapely import wkb

log = logging.getLogger(__name__)


class GeometryField(Field):
    pass


class PointField(GeometryField):
    widget = LatLonWidget()

    def __init__(self, *args, srid=4326, coordinate_type=None, **kwargs):
        self.srid = srid
        self.lon = None
        self.lat = None
        self.coordinate_type = coordinate_type
        super(PointField, self).__init__(*args, **kwargs)

    def _getpoint(self, lat, lon):
        if (lat is unset_value or lon is unset_value
                or lat is None or lon is None
                or lat == '' or lon == ''):
            return None
        point = "SRID={srid};POINT({lon} {lat})".format(
            lat=lat, lon=lon, srid=self.srid)
        log.debug("returning point for {lat}, {lon}: {point}".format(
            lat=lat, lon=lon, point=point))
        return point

    def process(self, formdata, data=unset_value, obj=None):
        latname = self.name+'_lat'
        lonname = self.name+'_lon'
        self.process_errors = []
        log.debug("Processing field {} with data: {}, obj: {} and formdata: {}"
                  .format(self.name, data, obj, formdata))
        if data is unset_value:
            log.debug('{} is unset value'.format(data))
            try:
                data = self.default()
            except TypeError:
                data = self.default
        elif data is not None:
            log.debug("Got data {} of type {}".format(data, data.__class__))
            log.debug("and keys: {}".format(data.keys()))
            if isinstance(data, WKBElement):
                geom = wkb.loads(bytes(data.data))
                data = {}
                data[lonname] = geom.x
                data[latname] = geom.y
                self.lon = geom.x
                self.lat = geom.y
            elif lonname in data and latname in data:
                self.lon = data[lonname]
                self.lat = data[latname]
                data[self.name] = self._getpoint(data[latname], data[lonname])

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata is not None:
            if lonname in formdata and latname in formdata:
                self.lon = formdata.get(lonname)
                self.lat = formdata.get(latname)
                self.raw_data = [self._getpoint(formdata.get(latname),
                                                formdata.get(lonname))]
                log.debug("Setting raw_data to {}".format(self.raw_data))
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

        try:
            for filter in self.filters:
                self.data = filter(self.data)
        except ValueError as e:
            self.process_errors.append(e.args[0])
        log.debug("Finished with object_data: {}".format(self.object_data))
