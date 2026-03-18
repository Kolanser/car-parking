from django.urls import path

from .views import CarClientCreateView, ParkingEventView, ParkingListView

urlpatterns = [
    path("", ParkingListView.as_view(), name="parking-list"),
    path("car-clients/", CarClientCreateView.as_view(), name="car-client-create"),
    path("<int:parking_id>/event/", ParkingEventView.as_view(), name="parking-event"),
]
