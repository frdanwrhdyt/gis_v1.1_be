from django.urls import path
from .views import (LayerView)


urlpatterns = [
    path('', LayerView.as_view(), name='layer')
]