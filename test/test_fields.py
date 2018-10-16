import logging
from unittest import TestCase
from flask_appbuilder import AppBuilder
from flask import Flask
from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from werkzeug.datastructures import MultiDict
from sqlalchemy import MetaData, create_engine
from flask_sqlalchemy import SQLAlchemy

codelog = logging.getLogger('fab_addon_geoalchemy')
codelog.setLevel(logging.DEBUG)

from fab_addon_geoalchemy.views import GeoModelView
from fab_addon_geoalchemy.models import GeoSQLAInterface
from fab_addon_geoalchemy.fields import PointField
from fab_addon_geoalchemy.widgets import LatLonWidget

cfg = {'SQLALCHEMY_DATABASE_URI': 'postgresql:///test',
       'CSRF_ENABLED': False,
       'WTF_CSRF_ENABLED': False,
       'SECRET_KEY': 'bla',
       'ADDON_MANAGERS': ['fab_addon_geoalchemy.manager.GeoAlchemyManager']}

app = Flask('testapp')
app.config.update(cfg)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata = MetaData(bind=engine)
db = SQLAlchemy(app, metadata=metadata)
db.session.commit()

appbuilder = AppBuilder(app, db.session)


class Observation(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    location2 = Column(Geometry(geometry_type='POINT', srid=3857))

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return 'Person Type %s' % self.id


class ObservationView(GeoModelView):
    datamodel = GeoSQLAInterface(Observation)
    add_columns = ['name', 'location', 'location2']
    show_columns = ['name', 'location', 'location2']


appbuilder.add_view(ObservationView, 'observations')
NL = 'SRID=4326;POLYGON((4.40108047690016 53.3586997019374,2.8607023099851' +\
     '51.4002188897169,6.9247420162497 50.6194989118665,7.67988543219077 ' +\
     '54.0188617734724,4.40108047690016 53.3586997019374))'

show_html = '<label>Latitude:</label> 1.0 <label>Longitude:</label> 4.0 ' +\
    '<div class="leaflet_map" id="location_map"></div>' +\
    '<script type="text/javascript">' +\
    'createROPointMap("location_map", 1.0, 4.0);</script>'


class TestFields(TestCase):
    def setUp(self):
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        ctx = app.app_context()
        ctx.push()
        db.create_all()
        db.session.add(Observation(name='something'))
        db.session.commit()
        db.session.flush()

    def test_unkown_column_is_point(self):
        interf = GeoSQLAInterface(Observation)
        self.assertFalse(interf.is_point("bla"))


    def test_show_widget(self):
        obs = Observation(name='test', location='SRID=4326;POINT(4 1)')
        db.session.add(obs)
        db.session.commit()
        db.session.flush()
        interf = GeoSQLAInterface(Observation)
        w = str(interf._get_attr_value(obs, 'location'))
        self.assertIsInstance(w, str)
        self.assertEqual(w, show_html)

    def test_manager_registration(self):
        self.assertEqual(list(appbuilder.addon_managers.keys()),
                         ['fab_addon_geoalchemy.manager.GeoAlchemyManager'])

    def test_additional_js_css(self):
        """
        Test if the js and css files are registered.
        """
        mgr = appbuilder.addon_managers[
            'fab_addon_geoalchemy.manager.GeoAlchemyManager']
        self.assertEqual(mgr.addon_js,
                         [('fab_addon_geoalchemy.static', 'js/leaflet.js'),
                          ('fab_addon_geoalchemy.static', 'js/main.js')])
        self.assertEqual(mgr.addon_css,
                         [('fab_addon_geoalchemy.static', 'css/leaflet.css'),
                          ('fab_addon_geoalchemy.static', 'css/map.css')])

    def testFieldConversion(self):
        form = ObservationView().add_form()
        self.assertTrue(hasattr(form, 'location'))
        self.assertIsInstance(form.location, PointField)
        self.assertIsInstance(form.location.widget, LatLonWidget)
        correct_html = 'Latitude: <input type="text" id="location_lat" ' +\
            'name="location_lat"> Longitude: <input type="text" ' +\
            'id="location_lon" name="location_lon">' +\
            '<div class="leaflet_map" id="location_map"></div>' +\
            '<script type="text/javascript">' +\
            'createPointMap("location_map","location_lat", "location_lon")' +\
            ';</script>'
        print(correct_html)
        widget = form.location()
        print(widget)
        self.assertEqual(widget, correct_html)

    def testDataProcessing(self):
        form = ObservationView().add_form()
        data = MultiDict({'name': 'test',
                          'location_lat': '52.34812',
                          'location_lon': '5.98193',
                          'location2_lat': '52.34812',
                          'location2_lon': '5.98193'})
        form.process(formdata=data)
        self.assertEqual(form.location.data,
                         'SRID=4326;POINT(5.98193 52.34812)')
        self.assertEqual(form.location2.data,
                         'SRID=3857;POINT(5.98193 52.34812)')
        row = Observation()
        form.populate_obj(row)
        db.session.add(row)
        print(row.location)
        db.session.commit()
        db.session.flush()
        print("Location: {}".format(row.location))
        print("Checking intersection")
        print(db.session.scalar(row.location.ST_Intersects(NL)))
        self.assertTrue(db.session.scalar(row.location.ST_Intersects(NL)))
        print("Finished checking intersection")
        db.session.commit()
        widget = form.location()
        correct_html = 'Latitude: <input type="text" id="location_lat" ' +\
            'name="location_lat" value="52.34812"> ' +\
            'Longitude: <input type="text" id="location_lon" ' +\
            'name="location_lon" value="5.98193">' +\
            '<div class="leaflet_map" id="location_map"></div>' +\
            '<script type="text/javascript">' +\
            'createPointMap("location_map","location_lat", "location_lon")' +\
            ';</script>'
        print(widget)
        print(correct_html)
        self.assertEqual(widget, correct_html)

    def testEmptyValue(self):
        form = ObservationView().add_form()
        data = MultiDict({'name': 'test',
                          'location_lat': '',
                          'location_lon': '',
                          'location2_lat': '52.34812',
                          'location2_lon': '5.98193'})
        form.process(formdata=data)
        self.assertEqual(form.location.data, None)
        self.assertEqual(form.location2.data,
                         'SRID=3857;POINT(5.98193 52.34812)')
        form.process(formdata=data)
        row = Observation()
        form.populate_obj(row)
        db.session.add(row)
        db.session.commit()
        db.session.flush()
        self.assertEqual(row.location, None)

    def testFormRefresh(self):
        print("Starting testFormRefresh")
        row = Observation(name='test',
                          location='SRID=4326;POINT(5.98193 52.34812)')
        db.session.add(row)
        db.session.commit()
        form = ObservationView().edit_form()
        db.session.commit()
        print("Got for {} with attributes {}".format(form, dir(form)))
        print("Getting new row")
        row = db.session.query(Observation).get(row.id)
        db.session.commit()
        print("Refreshing form")
        form = form.refresh(obj=row)
        print('Edit form: {}'.format(dir(form)))
        correct_html = 'Latitude: <input type="text" id="location_lat" ' +\
            'name="location_lat" value="52.34812"> ' +\
            'Longitude: <input type="text" id="location_lon" ' +\
            'name="location_lon" value="5.98193">' +\
            '<div class="leaflet_map" id="location_map"></div>' +\
            '<script type="text/javascript">' +\
            'createPointMap("location_map","location_lat", "location_lon")' +\
            ';</script>'
        widget = form.location()
        print(widget)
        print(correct_html)
        self.assertEqual(widget, correct_html)
        db.session.commit()
        print("Finished testFormRefresh")

    def tearDown(self):
        print("Starting drop_all")
        try:
            db.session.commit()
        except:
            pass
        db.drop_all()
        print("Finished")
