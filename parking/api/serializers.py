from rest_framework import serializers

from parking.models import Direction


class ParkingEventSerializer(serializers.Serializer):
    vehiclePlate = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=Direction.choices)
    brand = serializers.CharField(max_length=100, required=False, default="")
    model = serializers.CharField(max_length=100, required=False, default="")
