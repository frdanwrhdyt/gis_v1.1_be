import os
import glob
import zipfile
import geopandas as gpd
from sqlalchemy import create_engine
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .geo import geo, db  
from django.conf import settings
from utils.models import BaseModel

def validate_shp_extension(value):
    valid_extensions = ['.shp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f'Hanya file dengan ekstensi {", ".join(valid_extensions)} yang diizinkan.')

class Shp(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    feature = models.FileField(upload_to='%Y/%m/%d', blank=True, validators=[validate_shp_extension])

    def __str__(self):
        return self.name

@receiver(post_save, sender=Shp)
def publish_data(sender, instance, **kwargs):
    file = instance.feature.path
    file_path = os.path.dirname(file)
    conn_str = 'postgresql://postgres:T3lk0msat@10.83.253.52:5432/tsat_db'

    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(file_path)
    os.remove(file)

    shp_files = glob.glob(os.path.join(file_path, '*.shp'))
    
    try:
        gdf = gpd.read_file(shp_files[0])
        engine = create_engine(conn_str)
        gdf.to_postgis(con=engine, schema='data', name=instance.name, if_exists='replace')

        for shp_file in shp_files:
            os.remove(shp_file)
    except Exception as e:
        for shp_file in shp_files:
            os.remove(shp_file)
        instance.delete()
        print('Ada masalah saat mengunggah shp: ', e)

    geo.create_featurestore(store_name=settings.GEO_STORE, workspace=settings.GEO_WORKSPACE, db=settings.DB_NAME, host=settings.DB_HOST, pg_user=settings.DB_USERNAME, pg_password=settings.DB_PASSWORD, schema='data')
    geo.publish_featurestore(workspace=settings.GEO_WORKSPACE, store_name=settings.GEO_STORE, pg_table=instance.name)

@receiver(post_delete, sender=Shp)
def delete_data(sender, instance, **kwargs):
    db.delete_table(instance.name, schema='data')
    geo.delete_layer(instance.name, settings.GEO_WORKSPACE)
