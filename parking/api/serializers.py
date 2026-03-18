from rest_framework import serializers

from parking.models import CarClient, Direction, Parking, ParkingControl


class ParkingEventSerializer(serializers.Serializer):
    vehiclePlate = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=Direction.choices)
    brand = serializers.CharField(max_length=100, required=False, default="")
    model = serializers.CharField(max_length=100, required=False, default="")


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ["id", "address", "comment", "capacity"]


class ParkingControlSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="car_client.vehicle_plate")

    class Meta:
        model = ParkingControl
        fields = ["id", "vehicle_plate", "brand", "model", "entered_at", "exited_at"]


class CarClientSerializer(serializers.ModelSerializer):
    parkings = serializers.PrimaryKeyRelatedField(queryset=Parking.objects.all(), many=True)

    class Meta:
        model = CarClient
        fields = ["id", "vehicle_plate", "parkings"]

    def update(self, instance, validated_data):
        parkings = validated_data.pop("parkings", [])
        instance = super().update(instance, validated_data)
        instance.parkings.set(parkings)
        return instance
