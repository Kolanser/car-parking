from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import CarClient, ParkingControl

from .factories import CarClientFactory, ParkingControlFactory, ParkingFactory


def event_url(parking_id):
    return reverse("parking-event", kwargs={"parking_id": parking_id})


class ParkingListTest(APITestCase):
    def test_returns_all_parkings(self):
        ParkingFactory.create_batch(3)
        response = self.client.get(reverse("parking-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_response_fields(self):
        parking = ParkingFactory(address="ул. Пушкина, д. 1", capacity=10)
        response = self.client.get(reverse("parking-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(p for p in response.data if p["id"] == parking.pk)
        self.assertEqual(item["address"], "ул. Пушкина, д. 1")
        self.assertEqual(item["capacity"], 10)


class CarClientCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse("car-client-create")

    def test_creates_car_client_with_parkings(self):
        parking = ParkingFactory()
        response = self.client.post(self.url, {"vehicle_plate": "В123АА77", "parkings": [parking.pk]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        car = CarClient.objects.get(vehicle_plate="В123АА77")
        self.assertIn(parking, car.parkings.all())

    def test_creates_car_client_without_parkings(self):
        response = self.client.post(self.url, {"vehicle_plate": "С456ВВ77", "parkings": []})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CarClient.objects.filter(vehicle_plate="С456ВВ77").exists())

    def test_duplicate_plate_returns_400(self):
        CarClientFactory(vehicle_plate="Е789ОО77")
        response = self.client.post(self.url, {"vehicle_plate": "Е789ОО77", "parkings": []})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_parking_id_returns_400(self):
        response = self.client.post(self.url, {"vehicle_plate": "К000КК77", "parkings": [9999]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CarClientUpdateTest(APITestCase):
    def setUp(self):
        self.url = reverse("car-client-upsert")
        self.parking = ParkingFactory()

    def _put(self, plate, parkings):
        return self.client.put(self.url, {"plate": plate, "parkings": parkings}, format="json")

    def test_creates_new_car(self):
        response = self._put("А001АА77", [self.parking.pk])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CarClient.objects.filter(vehicle_plate="А001АА77").exists())

    def test_updates_existing_car(self):
        car = CarClientFactory(vehicle_plate="А002АА77")
        response = self._put("А002АА77", [self.parking.pk])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(car.parkings.values_list("pk", flat=True), [self.parking.pk])

    def test_clears_parkings(self):
        car = CarClientFactory(vehicle_plate="А003АА77")
        car.parkings.add(self.parking)
        response = self._put("А003АА77", [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(car.parkings.count(), 0)

    def test_empty_plate_returns_400(self):
        response = self._put("", [])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_parking_id_returns_400(self):
        response = self._put("А004АА77", [9999])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
