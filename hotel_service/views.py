from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

from datetime import date, datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from .models import Hotel, RoomType, Room, Amenity, HotelAmenity, RoomRate, Inventory
from users.permissions import IsAdminUserCustom
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model



from .serializers import (
    HotelSerializer,
    RoomTypeSerializer,
    RoomSerializer,
    AmenitySerializer,
    HotelAmenitySerializer,
    RoomRateSerializer,
    
)

class HotelListCreateAPIView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get(self, request, *args, **kwargs):
        cache_key = "hotel_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response
    
    def get_permissions(self):
          if self.request.method == 'GET':
              return [AllowAny()]
          return [IsAuthenticated(), IsAdminUserCustom()]
   

class HotelRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]

    def get(self, request, *args, **kwargs):
        cache_key = f"hotel_{kwargs['pk']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response

    def put(self, request, *args, **kwargs):
        cache_key = f"hotel_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on update
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        cache_key = f"hotel_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on delete
        return super().delete(request, *args, **kwargs)


class RoomTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
   

class RoomTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = f"roomtype_{kwargs['pk']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUserCustom()]
    
    def put(self, request, *args, **kwargs):
        cache_key = f"roomtype_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on update
        return super().put(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        cache_key = f"roomtype_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on delete
        return super().delete(request, *args, **kwargs)


class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = "room_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUserCustom()]
    
    def perform_create(self, serializer):
        with transaction.atomic():
            room = serializer.save()
            # Update inventory for the room's hotel and room type
            today = date.today()
            inventory, created = Inventory.objects.get_or_create(
            hotel_id=room.hotel_id,
            room_type_id=room.room_type_id,
            date=today,
            defaults={
                "total_count": 1,
                "booked_count": 0,
                "available_count": 1,
            },
            )
            if not created:
                inventory.total_count = F("total_count") + 1
                inventory.available_count = F("available_count") + 1
                inventory.save()
    
    

class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = f"room_{kwargs['pk']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response
    
  


class AmenityListCreateAPIView(generics.ListCreateAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = "amenity_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response


class AmenityRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = f"amenity_{kwargs['pk']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)


class HotelAmenityListCreateAPIView(generics.ListCreateAPIView):
    queryset = HotelAmenity.objects.all()
    serializer_class = HotelAmenitySerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):    
        cache_key = "hotelamenity_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUserCustom()]
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response


class HotelAmenityRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HotelAmenity.objects.all()
    serializer_class = HotelAmenitySerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]


class RoomRateListCreateAPIView(generics.ListCreateAPIView):
    queryset = RoomRate.objects.all()
    serializer_class = RoomRateSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = "roomrate_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        return response
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUserCustom()]
    


class RoomRateRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomRate.objects.all()
    serializer_class = RoomRateSerializer
    permission_classes = [IsAuthenticated(), IsAdminUserCustom()]
    def get(self, request, *args, **kwargs):
        cache_key = f"roomrate_{kwargs['pk']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    def put(self, request, *args, **kwargs):
        cache_key = f"roomrate_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on update
        return super().put(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        cache_key = f"roomrate_{kwargs['pk']}"
        cache.delete(cache_key)  # Invalidate cache on delete
        return super().delete(request, *args, **kwargs)



class InventorySummaryView(APIView):
    """
    Returns a summary of inventory per room type for a given date.
    If no date is provided via the query parameter "date" (YYYY-MM-DD),
    the summary will be generated for today's date.
    """
    def get(self, request, format=None):
        # Use the provided date or default to today.
        query_date = request.query_params.get("date", None)
        if query_date:
            try:
                query_date = datetime.strptime(query_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=400
                )
        else:
            query_date = date.today()

        # Get all inventory records for the specified date.
        inventories = Inventory.objects.filter(date=query_date)

        # Prepare a summary dictionary keyed by room type name.
        summary = {}
        for inv in inventories:
            # Retrieve the room type name.
            try:
                room_type = RoomType.objects.get(room_type_id=inv.room_type_id)
                room_type_name = room_type.name
            except RoomType.DoesNotExist:
                room_type_name = "Unknown"

            if room_type_name not in summary:
                summary[room_type_name] = {
                    "booked": 0,
                    "total": 0,
                    "available": 0
                }
            summary[room_type_name]["booked"] += inv.booked_count
            summary[room_type_name]["total"] += inv.total_count
            summary[room_type_name]["available"] += inv.available_count

        return Response(summary)
