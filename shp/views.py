from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .geo import geo

class LayerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = [] 

    def get(self, request):
        layers = geo.get_layers()
        return Response(layers, status=200)