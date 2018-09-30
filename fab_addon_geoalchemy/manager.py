import logging
from flask.ext.appbuilder.basemanager import BaseManager
from .views import ContactModelView
from flask_babelpkg import lazy_gettext as _


log = logging.getLogger(__name__)

"""
    Flask Appbuilder Addon Manager for Geoalchemy2
"""


class GeoAlchemyManager(BaseManager):


    def __init__(self, appbuilder):
        """
             Use the constructor to setup any config keys specific for your app. 
        """
        super(GeoAlchemyManager, self).__init__(appbuilder)
        #self.appbuilder.get_app.config.setdefault('MYADDON_KEY', 'SOME VALUE')

    def register_views(self):
        """
            This method is called by AppBuilder when initializing, use it to add you views
        """
        pass

    def pre_process(self):
        pass

    def post_process(self):
        pass

