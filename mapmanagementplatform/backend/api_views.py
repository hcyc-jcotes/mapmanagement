"""
API VIEWS HANDLE ALL THE FUNCTIONS AVAILABLE IN THE DJANGO REST API
"""

from .models import Region, Sequence, Coordinate_property
from rest_framework import generics
from datetime import date , datetime, timedelta
import pytz
from .serializers import CoordinatePropertySerializer, RegionSerializer, SequenceSerializer

# List the Coordinate properties on the API
class CoordinatePropertyView(generics.ListAPIView):
	serializer_class = CoordinatePropertySerializer

	def get_queryset(self):

		# Get URL parameter as a string, if exists
		ids = self.request.query_params.get('ids', None)
		minlon = self.request.query_params.get('min_lon', None)
		minlat = self.request.query_params.get('min_lat', None)
		maxlat = self.request.query_params.get('max_lat', None)
		maxlon = self.request.query_params.get('max_lon', None)
		datefrom = self.request.query_params.get('from',None)
		dateto = self.request.query_params.get('to',None)
		sequenceids = self.request.query_params.get('sequence_ids', None)

		# Get points for ids if they exist
		if ids is not None:
			# Convert parameter string to list of integers
			ids = [ int(x) for x in ids.split(',') ]
			# Get objects for all parameter ids 
			queryset = Coordinate_property.objects.filter(pk__in=ids)
		else:
			if minlon is not None and minlat is not None and maxlat is not None and maxlon is not None and datefrom is None and datefrom is None:
				queryset = Coordinate_property.objects.filter(longitude__gte=minlon, longitude__lte=maxlon, latitude__gte=minlat, latitude__lte=maxlat)
			else:
				if minlon is not None and minlat is not None and maxlat is not None and maxlon is not None and datefrom is not None and datefrom is not None:
					# Convert dates to Django Format
					dt_format = '%Y-%m-%d'  
					f = datetime.strptime(datefrom, dt_format).replace(tzinfo=pytz.UTC)
					t = datetime.strptime(dateto, dt_format).replace(tzinfo=pytz.UTC)
					t = t + timedelta(days=1)
					# Get sequences within the dates 
					coordinates = Coordinate_property.objects.filter(longitude__gte=minlon, longitude__lte=maxlon, latitude__gte=minlat, latitude__lte=maxlat).values('sequence_key').distinct()
					queryset = Sequence.objects.filter(captured_at__range=[f, t],pk__in=coordinates)
					queryset = Coordinate_property.objects.filter(sequence_key__in=queryset)
				else:
					if sequenceids is not None :
						sequenceids = [ int(x) for x in sequenceids.split(',') ]
						queryset = Coordinate_property.objects.filter(sequence_key__in=sequenceids)
					else:
						# Else no parameters, return all objects
						queryset = Coordinate_property.objects.all()
		return queryset


# List the Regions on the API
class RegionView(generics.ListAPIView):
	queryset = Region.objects.all()
	serializer_class = RegionSerializer


# List the Sequences on the API
class SequenceView(generics.ListAPIView):
	serializer_class = SequenceSerializer

	def get_queryset(self):

		# Get URL parameter as a string, if exists
		ids = self.request.query_params.get('ids', None)
		datefrom = self.request.query_params.get('from', None)
		dateto = self.request.query_params.get('to', None)
		minlon = self.request.query_params.get('min_lon', None)
		minlat = self.request.query_params.get('min_lat', None)
		maxlat = self.request.query_params.get('max_lat', None)
		maxlon = self.request.query_params.get('max_lon', None)
		coordinates_ids = self.request.query_params.get('coordinates_ids', None)

		# Get sequences for ids if they exist
		if ids is not None:
			# Convert parameter string to list of integers
			ids = [ int(x) for x in ids.split(',') ]
			# Get objects for all parameter ids 
			queryset = Sequence.objects.filter(pk__in=ids)
		else:
			if minlon is not None and minlat is not None and maxlat is not None and maxlon is not None and datefrom is None and datefrom is None:
				coordinates = Coordinate_property.objects.filter(longitude__gte=minlon, longitude__lte=maxlon, latitude__gte=minlat, latitude__lte=maxlat).values('sequence_key').distinct()
				queryset = Sequence.objects.filter(pk__in=coordinates)
			else:
				if datefrom is not None and dateto is not None and minlon is not None and minlat is not None and maxlat is not None and maxlon is not None:			
					# Convert dates to Django Format
					dt_format = '%Y-%m-%d'  
					f = datetime.strptime(datefrom, dt_format).replace(tzinfo=pytz.UTC)
					t = datetime.strptime(dateto, dt_format).replace(tzinfo=pytz.UTC)
					t = t + timedelta(days=1)
					# Get sequences within the dates 
					coordinates = Coordinate_property.objects.filter(longitude__gte=minlon, longitude__lte=maxlon, latitude__gte=minlat, latitude__lte=maxlat).values('sequence_key').distinct()
					queryset = Sequence.objects.filter(captured_at__range=[f, t],pk__in=coordinates)
				else:			
				# Else no parameters, return all objects
					queryset = Sequence.objects.all()
		return queryset
