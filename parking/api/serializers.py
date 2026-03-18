from rest_framework import serializers

from parking.models import CarClient, Direction, Parking


class ParkingEventSerializer(serializers.Serializer):
    vehiclePlate = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=Direction.choices)
    brand = serializers.CharField(max_length=100, required=False, default="")
    model = serializers.CharField(max_length=100, required=False, default="")


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ["id", "address", "comment", "capacity"]


class CarClientSerializer(serializers.ModelSerializer):
    parkings = serializers.PrimaryKeyRelatedField(queryset=Parking.objects.all(), many=True)

    class Meta:
        model = CarClient
        fields = ["id", "vehicle_plate", "parkings"]
