# fab_addon_geoalchemy

[![Build status](https://travis-ci.com/dolfandringa/fab_addon_geoalchemy.svg?branch=master)](https://travis-ci.com/dolfandringa/fab_addon_geoalchemy)

Implementation of GeoAlchemy fields for Flask Appbuilder.

It automatically transforms POINT Geometry columns to widgets with a field for latitude and longitude
and a leaflet map. The map has a pointer for the location, and there is two way binding where dragging 
the pointer changes the value in the input fields and vice-versa.
Later on, support for line and polygon columns may be added as well (pull requests welcome).

## Installation

Run `pip install fab-addon-geoalchemy`.

## Usage
You can find examples in the unittests in the tests folder.
But in short, this is what you need to do:

Add the following to your config.py:

```
ADDON_MANAGERS = ['fab_addon_geoalchemy.manager.GeoAlchemyManager']
```

And then use this for your models and views:


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

