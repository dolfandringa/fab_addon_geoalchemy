# fab_addon_geoalchemy
Implementation of GeoAlchemy fields for Flask Appbuilder.

It automatically transforms POINT Geometry columns to widgets with a field for latitude and longitude.
The goal is to add a leaflet widget and add support for line and polygon as well.

## Installation

Run `pip install fab-addon-geoalchemy`.

## Usage
You can find examples in the unittests in the tests folder.
But in short, this is what you need to do:

```
from sqlalchemy import Column, String
from fab_addon_geoalchemy.views import GeoModelView
from fab_addon_geoalchemy.models import GeoSQLAInterface, Geometry

class Observation(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(Geometry(geometry_type='POINT', srid=4326))

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return 'Person Type %s' % self.id


class ObservationView(GeoModelView):
    datamodel = GeoSQLAInterface(Observation)
    add_columns = ['name', 'location']

```

This will automatically create the LatLonWidget in the form, and process the data to transform the latitude and longitude values into a point geometry in the database. The srid form the column is used by the field for the conversion of the text coordinates to the geometry. No validation is done if the entered coordinates are actually valid for the specified SRID.
