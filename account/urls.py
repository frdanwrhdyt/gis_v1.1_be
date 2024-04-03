from django.urls import path
from .views import *

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user', UserView.as_view(), name='user'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('logout', BlacklistRefreshView.as_view(), name='logout')
]