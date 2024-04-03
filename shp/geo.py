from django.conf import settings
from geo.Geoserver import Geoserver
from pg.pg import Pg

db = Pg(dbname=settings.DB_NAME, user = settings.DB_USERNAME, password = settings.DB_PASSWORD, host = settings.DB_HOST, port = settings.DB_PORT)
geo = Geoserver(settings.GEO_HOST, username=settings.GEO_USERNAME, password=settings.GEO_PASSWORD)
