from django.urls import path

from .views import CarClientCreateView, CarClientUpdateView, ParkingEventView, ParkingListView

urlpatterns = [
    path("", ParkingListView.as_view(), name="parking-list"),
    path("car-clients/", CarClientCreateView.as_view(), name="car-client-create"),
    path("car-clients/update/", CarClientUpdateView.as_view(), name="car-client-upsert"),
    path("<int:parking_id>/event/", ParkingEventView.as_view(), name="parking-event"),
]
