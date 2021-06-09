"""
FOR MILESTONE 1 - TEAM 03

Serialize the models in the SQL DB to exposed them in the API
"""
from rest_framework import serializers
from .models import Coordinate_property, Region, Sequence

# Serialize the Coordinate property and expose the data from the db to the API for the front to consume
class CoordinatePropertySerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Coordinate_property
        fields = ('id', 'image_key', 'sequence_key', 'direction', 'neighbors', 'filename', 'coordinates',)
    def get_coordinates(self,obj):
      coordinate = obj.longitude, obj.latitude
      return coordinate

# Serialize the Region model
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

# Serialize the Sequence model
class SequenceSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()
    class Meta:
        model = Sequence
        fields = ('id', 'camera_make', 'captured_at', 'key', 'pano', 'points_in_seq', 'coordinates',)
    def get_coordinates(self,obj):
      coordinates = Coordinate_property.objects.filter(sequence_key=obj.id)
      y_coords = coordinates.values_list('latitude',flat = True)
      x_coords = coordinates.values_list('longitude',flat = True)
      coordinate = list(zip(x_coords,y_coords))
      return coordinate