from rest_framework import viewsets

from .models import Specialty
from .serializers import SpecialtySerializer


class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

