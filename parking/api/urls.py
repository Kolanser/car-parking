from django.urls import path

from .views import ParkingEventView

urlpatterns = [
    path("<int:parking_id>/event/", ParkingEventView.as_view(), name="parking-event"),
]
