from django.db import models
from rest_framework import serializers


class Direction(models.TextChoices):
    IN = "in", "Въезд"
    OUT = "out", "Выезд"


class ParkingEventSerializer(serializers.Serializer):
    vehiclePlate = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=Direction.choices)
    brand = serializers.CharField(max_length=100, required=False, default="")
    model = serializers.CharField(max_length=100, required=False, default="")
