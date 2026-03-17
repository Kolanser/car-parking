from django.contrib import admin

from .models import CarClient, Parking, ParkingControl


@admin.register(Parking)
class ParkingAdmin(admin.ModelAdmin):
    list_display = ("address", "capacity", "created_at")
    search_fields = ("address",)


@admin.register(CarClient)
class CarClientAdmin(admin.ModelAdmin):
    list_display = ("vehicle_plate", "created_at")
    search_fields = ("vehicle_plate",)
    filter_horizontal = ("parkings",)


@admin.register(ParkingControl)
class ParkingControlAdmin(admin.ModelAdmin):
    list_display = ("car_client", "parking", "brand", "model", "entered_at", "exited_at")
    list_filter = ("parking",)
    search_fields = ("car_client__vehicle_plate", "brand", "model")
    readonly_fields = ("entered_at",)
