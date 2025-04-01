from django.urls import path

from .views import (
    HotelListCreateAPIView,
    HotelRetrieveUpdateDestroyAPIView,
    RoomTypeListCreateAPIView,
    RoomTypeRetrieveUpdateDestroyAPIView,
    RoomListCreateAPIView,
    RoomRetrieveUpdateDestroyAPIView,
    AmenityListCreateAPIView,
    AmenityRetrieveUpdateDestroyAPIView,
    HotelAmenityListCreateAPIView,
    HotelAmenityRetrieveUpdateDestroyAPIView,
    RoomRateListCreateAPIView,
    RoomRateRetrieveUpdateDestroyAPIView,
    InventorySummaryView,
)

urlpatterns = [
    path('hotels/', HotelListCreateAPIView.as_view(), name='hotel-list-create'),
    path('hotels/<int:pk>/', HotelRetrieveUpdateDestroyAPIView.as_view(), name='hotel-detail'),
    path('room-types/', RoomTypeListCreateAPIView.as_view(), name='roomtype-list-create'),
    path('room-types/<int:pk>/', RoomTypeRetrieveUpdateDestroyAPIView.as_view(), name='roomtype-retrieve-update-destroy'),
    path('rooms/', RoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomRetrieveUpdateDestroyAPIView.as_view(), name='room-retrieve-update-destroy'),
    path('amenities/', AmenityListCreateAPIView.as_view(), name='amenity-list-create'),
    path('amenities/<int:pk>/', AmenityRetrieveUpdateDestroyAPIView.as_view(), name='amenity-retrieve-update-destroy'),
    path('hotel-amenities/', HotelAmenityListCreateAPIView.as_view(), name='hotelamenity-list-create'),
    path('hotel-amenities/<int:pk>/', HotelAmenityRetrieveUpdateDestroyAPIView.as_view(), name='hotelamenity-retrieve-update-destroy'),
    path('room-rates/', RoomRateListCreateAPIView.as_view(), name='roomrate-list-create'),
    path('room-rates/<int:pk>/', RoomRateRetrieveUpdateDestroyAPIView.as_view(), name='roomrate-retrieve-update-destroy'),
    path('inventory-summary/', InventorySummaryView.as_view(), name='inventory-summary'),
   
]