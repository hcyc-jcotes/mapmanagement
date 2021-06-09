from django.views.generic import View
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from .models import Region, User, Sequence, Coordinate_property
from django.utils import timezone
from django.db import IntegrityError
from django.db.models.base import ObjectDoesNotExist
from geographiclib.geodesic import Geodesic
from rest_framework import generics
#for near images calculation
from scipy.spatial import KDTree
from datetime import date
from django.conf import settings
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import time
import os 
import pickle
import math
import requests
import json
import urllib.request
import sqlite3
from .serializers import CoordinatePropertySerializer, RegionSerializer, SequenceSerializer
from django.db.models import Q
from utils.quadtree import Point, Rect, QuadTree
from utils.query_db import tree_builder,query_tree
import time


class CoordinatePropertyView(generics.ListAPIView):
	queryset = Coordinate_property.objects.all()
	serializer_class = CoordinatePropertySerializer

class RegionView(generics.ListAPIView):
	queryset = Region.objects.all()
	serializer_class = RegionSerializer

class SequenceView(generics.ListAPIView):
	queryset = Sequence.objects.all()
	serializer_class = SequenceSerializer

def quadtree(request):
	# DATA FROM DB USING DJANGO MODELS
	coordinates = Coordinate_property.objects.all().order_by('id')	
	data = []

	# EXTRACT id,longitude,latitude,direction
	for coordinate in coordinates:
		row_entry = [coordinate.id, coordinate.longitude, coordinate.latitude, coordinate.direction, coordinate.sequence_key_id]
		data.append(row_entry)
	# print(data)
	
	# # process data
	coords = np.array(data)
	print(coords[0])
	print(coords.shape)

	print("number of entries in db : ",len(coords))
	# make a local copy
	original_data = np.copy(coords)
	# print("original DT", type(original_data))
	# print(original_data)

	# drop ID. from coords
	coords = coords[:,1:3]
	print("coords[0]",coords[0])

	# Extract MAX and MIN values in long and lat
	max_long_lat = np.amax(coords, axis=0)
	print ("maxis = ",max_long_lat)
	min_long_lat = np.amin(coords, axis=0)
	print ("mins = ",type(min_long_lat))
	
	# normalize values
	normalize_long = 180.0
	normalize_lat  = 90.0

	tot_long= 360.0
	tot_lat = 180.0

	max_long = (max_long_lat[0]+normalize_long)
	max_lat  = (max_long_lat[1]+normalize_lat )

	min_long = (min_long_lat[0]+normalize_long)
	min_lat  = (min_long_lat[1]+normalize_lat )

	# print("min_max_long", min_long, max_long,"min_max_lat",min_lat,max_lat)

	coords[:,0] = (coords[:,0] + normalize_long)
	coords[:,1] = (coords[:,1] + normalize_lat )

	# print ("coords", coords)
	center_long = ((max_long + min_long) /2 )
	center_lat = ((max_lat + min_lat) /2 )

	points = [Point(*coord) for coord in coords]
	domain = Rect(center_long,center_lat,1,1)
	
	# BUILD TREE
	start_building_tree = time.process_time()
	gen_time = time.process_time() - start_building_tree

	qtree = QuadTree(domain, 300)
	for point in points:
		qtree.insert(point)
	gen_time = time.process_time() - start_building_tree
	print("gen time =",gen_time)
	print('Number of points in the domain =', len(qtree))

	factor = 10.0 ** 7
	for i in range (0,len(coords)):
		coords[i][0] = math.trunc(coords[i][0] * factor) / factor
		coords[i][1] = math.trunc(coords[i][1] * factor) / factor
		# print (coords[i][0],coords[i][1])

	# empty list initialized to store nearest neighbours
	fastest_nearest_neighbours_baby = []

	# QUERYING FOR ALL POINTS
	query_allpoints = time.process_time()
	for i,coordinate in zip(range(0,len(coords)),coordinates):
		# print(" i , id ",i,coordinates[i].id)
		found_points = []
		neighs = []
		lon  = coords[i][0]
		lat  = coords[i][1]
		# set query region with this.lat this.long as center and search area "0.0009"
		coord_region = Rect(lon, lat, 0.001, 0.001)    
		# QUERYING tree for this coordinate's NN
		qtree.query(coord_region, found_points)
		# QUERYING time for this coord's NearestNeighbours
		querying_nn_points_t = time.process_time()
		for j in range (0,len(found_points)):
			longi = found_points[j].x - 180
			lati  = found_points[j].y - 90
			factor= 10.0 ** 7
			longi = math.trunc (longi * factor) / factor
			lati  = math.trunc (lati * factor) / factor
			nn_object_qs = Coordinate_property.objects.filter(longitude__gte= longi-0.0000001 ,longitude__lte= longi+0.000001 ,latitude__gte =lati-0.1,latitude__lte=0.1).values('id','direction','sequence_key_id')
			nn_object_dir= Coordinate_property.objects.filter(longitude__gte= longi-0.0000001 ,longitude__lte= longi+0.000001 ,latitude__gte =lati-0.1,latitude__lte=0.1).values('direction')
			nn_obj_seqno = Coordinate_property.objects.filter(longitude__gte= longi-0.0000001 ,longitude__lte= longi+0.000001 ,latitude__gte =lati-0.1,latitude__lte=0.1).values('sequence_key_id')
			for nn_obj,nn_obj_dir,nn_seq_no in zip(nn_object_qs,nn_object_dir,nn_obj_seqno):
				nn_dir = nn_obj_dir['direction']
				nn_seq = nn_seq_no['sequence_key_id']
				anglediff = (original_data[i][3]-nn_dir + 180 + 360) % 360 - 180
				if (nn_obj['id'] not in neighs and anglediff <= 45 and anglediff>=-45):
					# CHECK FOR SEQUENCE NO IF THEY ARE FROM SAME SEQUENCE
					# if (int(original_data[i][4])!= nn_seq):
						neighs.append(nn_object_qs[0]['id'])
		querying_nn = time.process_time() - querying_nn_points_t
		print("\nquery time for coordinate,",i+1,"=",querying_nn)
		# SAVE NN for this coord in TABLE
		coordinate.QDneighbors = neighs
		coordinate.save()
		# fastest_nearest_neighbours_baby.append(neighs)
		# print(i+1,"neighs",fastest_nearest_neighbours_baby[i])
	# query_time = time.process_time() - query_allpoints
	# print("\nquery time for ",len(coords)," coordintes = ",query_time)

	return render(request,'qt.html')

def index(request):
	return render(request, 'index.html')

def home(request):
	return render(request, 'home.html')

def response(request):
	regions = Region.objects.all()
	return render(request,'response.html', context = {'regions': regions})

def angleFromCoordinate(lat1, long1, lat2, long2):
	dLon = (long2 - long1)
	x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
	y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
	bearing = math.atan2(x,y)   
	bearing = math.degrees(bearing)
	bearing = (bearing + 360) % 360
	return bearing

def angleFromCoordinateLib(lat1, lng1, lat2, lng2):
	geod = Geodesic.WGS84
	bearing = geod.Inverse(lat1,lng1,lat2,lng2)
	bearing = (bearing['azi1'] + 360) % 360
	return bearing

def calcNSEW(lat1, long1, lat2, long2):
	points = ["North", "North east", "East", "South east", "South", "South west", "West", "North west"]
	bearing = angleFromCoordinate(lat1, long1, lat2, long2)
	bearing += 22.5
	bearing = bearing % 360
	bearing = int(bearing / 45) # values 0 to 7
	NSEW = points [bearing]
	return NSEW

def calcerror(angle1, angle2):
	angle = abs(angle1-angle2);
	if (angle > 180):
		angle = 360 - angle
	angle = angle/360	
	return angle

def getdirection(request):
	sequences = Sequence.objects.all().order_by('id')
	#LOOP THROUGH ALL THE SEQUENCES
	for sequencetosearch in sequences:		
		coordinates = Coordinate_property.objects.filter(sequence_key = sequencetosearch).order_by('id')
		lastcoordinate = Coordinate_property.objects.filter(sequence_key = sequencetosearch).order_by('id').last()
		previousdirection = 0
		#LOOP THROUGH THE COORDINATES FROM THE SEQUENCE
		for coordinate in coordinates:
			#CASE LAST COORDINATE FROM THE PARTICULAR SEQUENCE
			if coordinate == lastcoordinate:
				coordinate.direction = previousdirection
				coordinate.cardinaldirection = previouscardinal
				coordinate.errorfromca = calcerror(coordinate.direction,coordinate.ca)
				coordinate.directionchanges = 0
			#OTHER CASES	
			else:
				lat1 = coordinate.latitude
				long1 = coordinate.longitude				
				nextcoordinate = Coordinate_property.objects.filter(id__gt = coordinate.id).order_by('id').first()
				lat2 = nextcoordinate.latitude
				long2 = nextcoordinate.longitude
				coordinate.direction = angleFromCoordinateLib(lat1, long1, lat2, long2)
				coordinate.cardinaldirection = calcNSEW(lat1, long1, lat2, long2)
				if(coordinate.direction == 0):
					coordinate.direction = previousdirection
					coordinate.cardinaldirection = previouscardinal
				if(previousdirection == 0):
					coordinate.directionchanges = 0
				else:
					coordinate.directionchanges = coordinate.direction - previousdirection	
				previousdirection = coordinate.direction
				previouscardinal = coordinate.cardinaldirection
				coordinate.errorfromca = calcerror(coordinate.direction,coordinate.ca)
			print(coordinate.id)			
			coordinate.save()
	return render('directions.html')

def searchnearest(request):
	start_time = time.time()
	coordinates = Coordinate_property.objects.all().order_by('id')	
	y_coords = coordinates.values_list('latitude',flat = True)
	x_coords = coordinates.values_list('longitude',flat = True)
	distanced = 100 #In meters
	distanced = (distanced/(6371000*math.pi))*180 # Transform it into the eucledian distance
	v = pd.DataFrame(list(zip(x_coords,y_coords)),columns=['latitude','longitude']) 
	kdtree = KDTree(v, leafsize = 10) #creates the KDTREE

	for coordinate in coordinates:
		lat = coordinate.latitude
		lon = coordinate.longitude
		angle = coordinate.direction
		
		distances, ind = kdtree.query((coordinate.longitude,coordinate.latitude),k=30) #QUERY THE TREE
		#print('the closest point to: ' + str(lon) + ',' + str(lat) + ' with a distance of ' + str(distance) +  ' meters angle: ' + str(angle) + ' are:')
		indextostore = []		
		for i,distance in zip(ind,distances):
			index = i + 1
			point = coordinates.get(id=index)
			anglediff = min(abs(point.direction - angle), 360 - abs(angle - point.direction));
			if (anglediff <= 45 and distance <= distanced): #max comparable angle
				#print('id: ' + str(index) + " imageKey: " + str(point.image_key) + " sequencekey: " + str(point.sequence_key) + ' located at: ' + str(point.longitude) + ' , '+ str(point.latitude) + 
				#' with an angle of: '+ str(point.direction) + '°')
				indextostore.append(index)
		# print(coordinate.id)
		coordinate.neighbors = indextostore
		coordinate.save()
	print("--query time- %s seconds ---" %(time.time() - start_time))

	return render(request, 'index.html')

def sequences(request):
	regions = Region.objects.all()
	region = regions.get(id = 1)	 
	url = 'https://a.mapillary.com/v3/sequences'
	client_id = 'dm95M3VFaHJkZ2dDS1RDZzlaVXN1RjpkMDU4NTU5ZDdhMDM4MmZi'
	start_time = region.last_update.strftime("%Y-%m-%d")
	print(start_time)
	per_page = 1000
	bbox = str(region.min_longitude) + ','+ str(region.min_latitude) + ',' + str(region.max_longitude) + ',' + str(region.max_latitude)
	PARAMS = {'client_id': client_id, 'bbox': bbox, 'per_page': per_page, 'start_time' : start_time}
	response = requests.get(url, params = PARAMS, headers={'Content-Type': 'application/json'})
	print(response.url)	
	url = response.links["first"]["url"]
	first_run = True 
	counter = 1
	counter_newdata = 0
	while url is not None:	
		if(first_run):			
			response = requests.get(url, headers={'Content-Type': 'application/json'})
			print(str(counter) + ' run')
		else:
			try:
				url = response.links["next"]["url"]
				response = requests.get(url, headers={'Content-Type': 'application/json'})
				counter += 1
				print(url)
				print(str(counter) + ' run')
			except:
				break
		first_run = False
		imagesFromAPI = json.loads(response.content.decode('utf-8'))
		features = imagesFromAPI['features']	
		for sequenceLoad in features:			
			camera_makeJ = sequenceLoad['properties']['camera_make']
			captured_atJ = sequenceLoad['properties']['captured_at']
			created_atJ = sequenceLoad['properties']['created_at']
			keyJ = sequenceLoad['properties']['key']
			panoJ = sequenceLoad['properties']['pano']
			user_keyJ = sequenceLoad['properties']['user_key']
			user = User.objects.get(key = user_keyJ)			
			region_keyJ = regions[0]
			stored_atJ = timezone.now()
			coordinatesJ = sequenceLoad['geometry']['coordinates']
			casJ = sequenceLoad['properties']['coordinateProperties']['cas']
			image_keysJ = sequenceLoad['properties']['coordinateProperties']['image_keys']
			points_in_seqJ = len(coordinatesJ)
			print(keyJ)
			sequenceTostore = Sequence(camera_make = camera_makeJ, captured_at = captured_atJ, created_at = created_atJ,
					key = keyJ, pano = panoJ, user_key = user, region_key = region_keyJ, stored_at = stored_atJ, points_in_seq = points_in_seqJ)
			try:
				sequenceTostore.save()
				sequenceJ = Sequence.objects.get(key = keyJ)
				for imagetaken, casTaken, coordinatesTaken in zip(image_keysJ, casJ, coordinatesJ):
					caJ = casTaken
					longitudeJ = coordinatesTaken[0]
					latitudeJ = coordinatesTaken[1]
					image_keyJ = imagetaken		
					one = Coordinate_property(ca = caJ, image_key = image_keyJ, longitude = longitudeJ, latitude = latitudeJ,
						sequence_key = sequenceJ)
					one.save()
					counter_newdata += 1
			except IntegrityError: 
				continue
	region.last_update = timezone.now()
	region.save()
	print(str(counter_newdata) + ' new points had been stored.')			
	return render(request,'sequences.html')


def users(request):
	regions = Region.objects.all()
	url = 'https://a.mapillary.com/v3/users'
	client_id = 'dm95M3VFaHJkZ2dDS1RDZzlaVXN1RjpkMDU4NTU5ZDdhMDM4MmZi'
	bbox = str(regions[0].min_longitude) + ','+ str(regions[0].min_latitude) + ',' + str(regions[0].max_longitude) + ',' + str(regions[0].max_latitude)
	PARAMS = {'client_id': client_id, 'bbox': bbox}
	response = requests.get(url, params = PARAMS, headers={'Content-Type': 'application/json'})	
	url = response.links["first"]["url"]
	first_run = True 
	counter = 1
	while url is not None:	
		if(first_run):			
			response = requests.get(url, headers={'Content-Type': 'application/json'})
			print(str(counter) + ' run')
		else:
			try:
				url = response.links["next"]["url"]
				response = requests.get(url, headers={'Content-Type': 'application/json'})
				counter += 1
				print(str(counter) + ' run')
			except:
				break
		first_run = False
		usersFromApi = json.loads(response.content.decode('utf-8'))
		for user in usersFromApi:
			aboutJ = user.get('about', '')
			avatarJ = user['avatar'] 
			created_atJ = user['created_at']	
			keyJ = user['key']
			usernameJ = user['username']
			stored_atJ = timezone.now()					
			one = User(about = aboutJ, avatar = avatarJ, created_at = created_atJ, key = keyJ,
				username = usernameJ, stored_at = stored_atJ)
			one.save()
	return render(request,'users.html')
