from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import ParkingControl

from .factories import CarClientFactory, ParkingControlFactory, ParkingFactory


def event_url(parking_id):
    return reverse("parking-event", kwargs={"parking_id": parking_id})


class ParkingEventEntryTest(APITestCase):
    def setUp(self):
        self.parking = ParkingFactory(capacity=2)
        self.car = CarClientFactory()
        self.car.parkings.add(self.parking)

    def _post(self, plate, direction="in", **kwargs):
        return self.client.post(
            event_url(self.parking.pk),
            {"vehiclePlate": plate, "direction": direction, **kwargs},
        )

    def test_entry_creates_record(self):
        response = self._post(self.car.vehicle_plate)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ParkingControl.objects.filter(car_client=self.car, exited_at__isnull=True).exists())

    def test_parking_not_found(self):
        response = self.client.post(event_url(9999), {"vehiclePlate": "X000XX77", "direction": "in"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_car_not_in_whitelist(self):
        other_car = CarClientFactory()
        response = self._post(other_car.vehicle_plate)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_car_unknown_plate(self):
        response = self._post("UNKNOWN99")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_free_spots(self):
        parking = ParkingFactory(capacity=1)
        car1 = CarClientFactory()
        car2 = CarClientFactory()
        car1.parkings.add(parking)
        car2.parkings.add(parking)
        ParkingControlFactory(car_client=car1, parking=parking)

        response = self.client.post(event_url(parking.pk), {"vehiclePlate": car2.vehicle_plate, "direction": "in"})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_direction(self):
        response = self._post(self.car.vehicle_plate, direction="not_a_direction")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ParkingEventExitTest(APITestCase):
    def setUp(self):
        self.parking = ParkingFactory()
        self.car = CarClientFactory()
        self.car.parkings.add(self.parking)

    def test_exit_closes_record(self):
        ParkingControlFactory(car_client=self.car, parking=self.parking)
        response = self.client.post(
            event_url(self.parking.pk),
            {"vehiclePlate": self.car.vehicle_plate, "direction": "out"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record = ParkingControl.objects.get(car_client=self.car, parking=self.parking)
        self.assertIsNotNone(record.exited_at)

    def test_exit_without_active_record(self):
        response = self.client.post(
            event_url(self.parking.pk),
            {"vehiclePlate": self.car.vehicle_plate, "direction": "out"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
