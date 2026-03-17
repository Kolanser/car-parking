from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parking.models import CarClient, Parking, ParkingControl, Direction

from .serializers import ParkingEventSerializer


class ParkingEventView(APIView):
    def post(self, request, parking_id):
        try:
            parking = Parking.objects.get(pk=parking_id)
        except Parking.DoesNotExist:
            return Response({"detail": "Парковка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParkingEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        vehicle_plate = data["vehiclePlate"]
        direction = data["direction"]

        try:
            car_client = CarClient.objects.get(vehicle_plate=vehicle_plate)
        except CarClient.DoesNotExist:
            return Response(
                {"detail": "Автомобиль не найден в белом списке."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not car_client.parkings.filter(pk=parking_id).exists():
            return Response(
                {"detail": "Автомобиль не имеет доступа к этой парковке."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if direction == Direction.IN:
            return self._handle_entry(parking, car_client, data)
        else:
            return self._handle_exit(parking, car_client)

    def _handle_entry(self, parking, car_client, data):
        active_count = ParkingControl.objects.filter(parking=parking, exited_at__isnull=True).count()
        if active_count >= parking.capacity:
            return Response(
                {"detail": "На парковке нет свободных мест."},
                status=status.HTTP_409_CONFLICT,
            )
        ParkingControl.objects.create(
            car_client=car_client,
            parking=parking,
            brand=data["brand"],
            model=data["model"],
        )
        return Response(
            {"detail": "Въезд зафиксирован."},
            status=status.HTTP_201_CREATED,
        )

    def _handle_exit(self, parking, car_client):
        parking_control = (
            ParkingControl.objects.filter(
                car_client=car_client,
                parking=parking,
                exited_at__isnull=True,
            )
            .order_by("-entered_at")
            .first()
        )
        if not parking_control:
            return Response(
                {"detail": "Автомобиль не найден на парковке."},
                status=status.HTTP_404_NOT_FOUND,
            )
        parking_control.exited_at = timezone.now()
        parking_control.save(update_fields=["exited_at"])
        return Response(
            {"detail": "Выезд зафиксирован."},
            status=status.HTTP_200_OK,
        )
