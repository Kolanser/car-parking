from django.db import models


class TimestampMixin(models.Model):
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        abstract = True


class Parking(TimestampMixin):
    address = models.CharField("адрес", max_length=500)
    comment = models.TextField("комментарий", blank=True)
    capacity = models.PositiveIntegerField("вместимость")

    class Meta:
        verbose_name = "Парковка"
        verbose_name_plural = "Парковки"

    def __str__(self):
        return f"{self.address}"


class CarClient(TimestampMixin):
    vehicle_plate = models.CharField("государственный регистрационный номер", max_length=20, unique=True)
    parkings = models.ManyToManyField(Parking, related_name="allowed_cars", blank=True, verbose_name="парковки")

    class Meta:
        verbose_name = "Автомобиль клиента"
        verbose_name_plural = "Автомобили клиентов"

    def __str__(self):
        return self.vehicle_plate


class ParkingControl(TimestampMixin):
    car_client = models.ForeignKey(
        CarClient, on_delete=models.PROTECT, related_name="sessions", verbose_name="автомобиль клиента"
    )
    parking = models.ForeignKey(
        Parking, on_delete=models.PROTECT, related_name="sessions", verbose_name="парковка"
    )
    brand = models.CharField("марка", max_length=100, blank=True)
    model = models.CharField("модель", max_length=100, blank=True)
    entered_at = models.DateTimeField("время въезда", auto_now_add=True)
    exited_at = models.DateTimeField("время выезда", null=True, blank=True)

    class Meta:
        verbose_name = "Контроль парковки"
        verbose_name_plural = "Контроль парковки"

    def __str__(self):
        return f"{self.car_client} @ {self.parking} ({self.entered_at})"
