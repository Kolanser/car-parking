import factory

from parking.models import CarClient, Parking, ParkingControl


class ParkingFactory(factory.django.DjangoModelFactory):
    address = factory.Sequence(lambda n: f"ул. Тестовая, д. {n}")
    capacity = factory.Faker("random_int", min=1)

    class Meta:
        model = Parking


class CarClientFactory(factory.django.DjangoModelFactory):
    vehicle_plate = factory.Sequence(lambda n: f"A{n:03d}BC77")

    class Meta:
        model = CarClient


class ParkingControlFactory(factory.django.DjangoModelFactory):
    car_client = factory.SubFactory(CarClientFactory)
    parking = factory.SubFactory(ParkingFactory)
    brand = factory.Faker("word")
    model = factory.Faker("word")

    class Meta:
        model = ParkingControl
