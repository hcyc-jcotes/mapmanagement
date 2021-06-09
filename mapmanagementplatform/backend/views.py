"""
FOR MILESTONE 1 - TEAM 03

VIEWS HANDLES ALL THE FUNCTIONS AVAILABLE IN THE BACKEND
"""
from django.views.generic import View
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from .models import Region, User, Sequence, Coordinate_property
from django.utils import timezone
from django.db import IntegrityError
from django.db.models.base import ObjectDoesNotExist
from geographiclib.geodesic import Geodesic
# from rest_framework import generics
#for near images calculation
from scipy.spatial import KDTree
from datetime import date , datetime, timedelta
from django.conf import settings
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import pytz
import time
import os 
import pickle
import math
import requests
import json
import urllib.request
import sqlite3
import sys

import sys
import sqlite3
import urllib.request
import datetime
import threading

import io
import shutil
import sys
from multiprocessing.pool import ThreadPool
import pathlib
from PIL import Image
import time
from .serializers import CoordinatePropertySerializer, RegionSerializer, SequenceSerializer
from utils.quadtree import Point, Rect, QuadTree

#Home site
def home(request):
	return render(request, 'home.html')

	#Display latest information of the region (BBOX and last updated)
def response(request):
	regions = Region.objects.all()
	return render(request,'response.html', context = {'regions': regions})

	#Calculate the angle between to two points, NOT USED
def angleFromCoordinate(lat1, long1, lat2, long2):
	dLon = (long2 - long1)
	x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
	y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
	bearing = math.atan2(x,y)   
	bearing = math.degrees(bearing)
	bearing = (bearing + 360) % 360
	return bearing

	#Calculate the angle between to two points using the Geodesic library, currently used 
def angleFromCoordinateLib(lat1, lng1, lat2, lng2):
	geod = Geodesic.WGS84
	bearing = geod.Inverse(lat1,lng1,lat2,lng2)
	bearing = (bearing['azi1'] + 360) % 360
	return bearing

	#Calculate the Cardinal direction between two points, NOT USED
def calcNSEW(lat1, long1, lat2, long2):
	points = ["North", "North east", "East", "South east", "South", "South west", "West", "North west"]
	bearing = angleFromCoordinate(lat1, long1, lat2, long2)
	bearing += 22.5
	bearing = bearing % 360
	bearing = int(bearing / 45) # values 0 to 7
	NSEW = points [bearing]
	return NSEW

	#Calculate the error comparing the cas with the estimated direction, NOT USED
def calcerror(angle1, angle2):
	angle = abs(angle1-angle2)
	if (angle > 180):
		angle = 360 - angle
	angle = angle/360	
	return angle 

def deltaneighbors():
	print("GETTING NEW VALUES FROM DB.")
	newcoordinates = Coordinate_property.objects.filter(neighbors__isnull=True).order_by('id')
	data =[]
	newdata =[]
	print("FOUND", len(newcoordinates),"NEW COORDINATES" )
	if len(newcoordinates) > 0:
		print("GETTING ALL VALUES FROM DB.")
		coordinates = Coordinate_property.objects.all().order_by('id')
		print("FOUND", len(coordinates),"COORDINATES" )
		for coordinate in coordinates:
			row_entry = [coordinate.id, coordinate.longitude, coordinate.latitude, coordinate.direction, coordinate.sequence_key_id,coordinate.neighbors]
			data.append(row_entry)
		for newcoordinate in newcoordinates:
			newrow_entry = [newcoordinate.id, newcoordinate.longitude, newcoordinate.latitude, newcoordinate.direction, newcoordinate.sequence_key_id]
			newdata.append(newrow_entry)
		# PROCESS DATA
		coords = np.array(data)
		newcoords = np.array(newdata)
		# MAKE A LOCAL COPY IN MEMORY
		original_data = np.copy(coords)
		neworiginal_data = np.copy(newcoords)
		# STORE POINTS(id,long,lat)
		p_coords = coords[:,0:3] 
		# DROP ID, etc f`rom coords
		coords = coords[:,1:3]
		# SETTING DOMAIN NOW,
		# TIME FOR DOMAIN GENERATION AND LOAD
		start_domain_load = time.process_time()
		# EXTRACT MAX and MIN values in long and lat
		max_long_lat,min_long_lat = np.amax(coords, axis=0), np.amin(coords, axis=0)
		# NORMALIZE VALUES OF LAT, LONG AS DOMAIN CAN HANDLE ONLY +VE VALUES
		normalize_long,normalize_lat = 180.0,90.0
		tot_long,tot_lat = 360.0,180.0
		max_long,max_lat = (max_long_lat[0]+normalize_long),(max_long_lat[1]+normalize_lat )
		min_long,min_lat = (min_long_lat[0]+normalize_long), (min_long_lat[1]+normalize_lat )
		coords[:,0],coords[:,1] = (coords[:,0] + normalize_long),(coords[:,1] + normalize_lat )
		# CENTER DOMAIN AT CENTROID OF THE RECTANGLE BOUNDING ALL POINTS IN DB
		center_long = ((max_long + min_long) /2 )
		center_lat = ((max_lat + min_lat) /2 )
		domain = Rect(center_long,center_lat,500,500)
		# TOTAL TIME TO GENERATE AND LOAD DOMAIN
		domain_load_time = time.process_time() - start_domain_load
		print("TOTAL TIME TO GENERATE AND LOAD DOMAIN FROM VALUES IN DB =",domain_load_time)
		# GENERATE POINTS TO BE FED TO QUADTREE
		start_generatin_points = time.process_time()
		points = [Point(*coordsp) for coordsp in p_coords]
		points_load_time = time.process_time() - start_generatin_points
		# BUILD TREE AND INSERT POINTS
		start_building_tree = time.process_time()
		qtree = QuadTree(domain, 50)
		gen_time = time.process_time() - start_building_tree
		# INSERT POINTS INTO TREE
		start = time.process_time()
		for point in points:
			qtree.insert(point)
		insertion_time = time.process_time() - start
		print("TIME TO INSERT ALL POINTS  =",insertion_time)
		print('TOTAL POINTS IN TREE = ', len(qtree))
		# SET PRECISION TO 7 places after decimal
		factor = 10.0 ** 7
		coords[:,0] = np.trunc(coords[:,0] * factor) / factor
		coords[:,1] = np.trunc(coords[:,1] * factor) / factor
		# QUERYING FOR ALL NEW POINTS
		query_allpoints = time.process_time()
		for ncoordinate in newcoordinates:
			if ncoordinate.id %100 ==0 :
				print ("CHECKING FOR ",ncoordinate.id,"th COORDINATE. QUERY TIME TILL NOW = ",
				time.process_time()-query_allpoints,"SECONDS")
			found_points = []
			distanced_neighbors = []
			neighs = []
			i = int(ncoordinate.id-1)
			# LOAD VALUES FOR DIRECTION AND SEQ.NO. OF QUERY POINT FROM ORIGINAL DATA
			lon  = coords[i][0]
			lat  = coords[i][1]
			dir_querypt  = original_data[i][3]
			seq_querypt  = original_data[i][4]
			# SET QUERY REGION OF SEARCH AREA OF "0.001 X 0.001" CENTERED AT LON,LAT AND
			coord_region = Rect(lon, lat, 0.001, 0.001) 
			# LOG QUERY TIME FOR FINDING i'th NN POINTS
			querying_nn_points_t = time.process_time()   
			# QUERY TREE FOR i'th POINTS(lon,lat) NN
			qtree.query(coord_region, found_points)
			final_neigh=[i+1]
			# Got ID'S OF i'th points Nearesst Neighbours
			# Filter these considering direction,ditance and seq. no.
			for j in range (0,len(found_points)):
				# SELECT ID OF NN POINT OF QUERY POINT
				id = found_points[j]
				# GET ALL METADATA FROM ORIGINAL_DATA FOR THIS NEAREST NEIGHBOUR TO FIYLTER IT  
				# id-1 because numpy array location starts with 0
				longitu = original_data[id-1][1]
				latitu  = original_data[id-1][2]
				diru    = original_data[id-1][3]
				sequ    = original_data[id-1][4]
				if(diru != None and dir_querypt!= None ):
					# CALCULATE ANGLE CHANGE in ViEW DIRECTION
					anglediff = (original_data[id-1][3]-dir_querypt + 180 + 360) % 360 - 180
					if (anglediff <= 45 and anglediff>=-45):
						# CHECK FOR SEQUENCE NO
						if (sequ!= seq_querypt):
							distance =  points[i].distance_to(points[id-1])
							distanced_neighbours = [distance,id]
							neighs.append(distanced_neighbours)
				else:
					 print("Missing direction values for id : ",id," or ",i+1)
			sorted_neighs=sorted(neighs)
			final_neigh+=[x[1] for x in sorted_neighs]
			querying_nn = time.process_time() - querying_nn_points_t
			ncoordinate.neighbors = final_neigh
			ncoordinate.save()
		query_time = time.process_time() - query_allpoints
		print("\n TOTAL TIME TO FIND NEAREST NEIGHBOUR OF ",len(newcoordinates)," COORDINATES = ",query_time)
	else:
		print ("NO NEW DATA AVAILABLE")
 

def neighbors():
	# TIME FOR LOADING DATA
	start_data_load = time.process_time()
	# LOAD DATA FROM DB USING DJANGO MODELS
	print("GETTING VALUES FROM DB.")
	coordinates = Coordinate_property.objects.all().order_by('id')	
	print("FOUND ",len(coordinates)," COORDINATES.")
	data = []
	# EXTRACT id,longitude,latitude,direction
	for coordinate in coordinates:
		row_entry = [coordinate.id, coordinate.longitude, coordinate.latitude, coordinate.direction, coordinate.sequence_key_id]
		data.append(row_entry)	
	# PROCESS DATA
	coords = np.array(data)
	# MAKE A LOCAL COPY IN MEMORY
	original_data = np.copy(coords)
	# STORE POINTS(id,long,lat)
	p_coords = coords[:,0:3] 
	# DROP ID, etc from coords
	coords = coords[:,1:3]
	# SETTING DOMAIN 
	# TIME FOR DOMAIN GENERATION AND LOAD
	start_domain_load = time.process_time()
	# EXTRACT MAX and MIN values in long and lat
	max_long_lat,min_long_lat = np.amax(coords, axis=0), np.amin(coords, axis=0)
	# NORMALIZE VALUES OF LAT, LONG AS DOMAIN CAN HANDLE ONLY +VE VALUES
	normalize_long,normalize_lat = 180.0,90.0
	tot_long,tot_lat = 360.0,180.0
	max_long,max_lat = (max_long_lat[0]+normalize_long),(max_long_lat[1]+normalize_lat )
	min_long,min_lat = (min_long_lat[0]+normalize_long), (min_long_lat[1]+normalize_lat )
	coords[:,0],coords[:,1] = (coords[:,0] + normalize_long),(coords[:,1] + normalize_lat )
	# CENTER DOMAIN AT CENTROID OF THE RECTANGLE BOUNDING ALL POINTS IN DB
	center_long = ((max_long + min_long) /2 )
	center_lat = ((max_lat + min_lat) /2 )
	# For larger number of NN increase search size by setting Rect args 1 and 2 for hright and width respectively
	domain = Rect(center_long,center_lat,500,500)
	# TOTAL TIME TO GENERATE AND LOAD DOMAIN
	domain_load_time = time.process_time() - start_domain_load
	print("TOTAL TIME TO GENERATE AND LOAD DOMAIN FROM VALUES IN DB =",domain_load_time)
	# GENERATE POINTS TO BE FED TO QUADTREE
	start_generatin_points = time.process_time()
	points = [Point(*coordsp) for coordsp in p_coords]
	points_load_time = time.process_time() - start_generatin_points
	# BUILD TREE AND INSERT POINTS
	start_building_tree = time.process_time()
	qtree = QuadTree(domain, 50)
	gen_time = time.process_time() - start_building_tree
	# INSERT POINTS INTO TREE
	start = time.process_time()
	for point in points:
		qtree.insert(point)
	insertion_time = time.process_time() - start
	print("TIME TO INSERT ALL POINTS  =",insertion_time)
	print('TOTAL POINTS IN TREE =', len(qtree))
	# SET PRECISION TO 7 places after decimal
	factor = 10.0 ** 7
	coords[:,0] = np.trunc(coords[:,0] * factor) / factor
	coords[:,1] = np.trunc(coords[:,1] * factor) / factor
	# QUERYING FOR ALL POINTS
	query_allpoints = time.process_time()
	for i,coordinate in zip(range(0,len(coords)),coordinates):
		if(i%4000 == 0):
			print ("CHECKING FOR ",i, "th COORDINATE QUERY TIME TILL NOW = ",
			time.process_time()-query_allpoints,"SECONDS")
		found_points = []
		distanced_neighbors = []
		neighs = []
		# LOAD VALUES FOR DIRECTION AND SEQ.NO. OF QUERY POINT FROM ORIGINAL DATA
		lon  = coords[i][0]
		lat  = coords[i][1]
		dir_querypt  = original_data[i][3]
		seq_querypt  = original_data[i][4]
		# SET QUERY REGION OF SEARCH AREA OF "0.001 X 0.001" CENTERED AT LON,LAT AND
		coord_region = Rect(lon, lat, 0.001, 0.001) 
		# LOG QUERY TIME FOR FINDING i'th NN POINTS
		querying_nn_points_t = time.process_time()   
		# QUERY TREE FOR i'th POINTS(lon,lat) NN
		qtree.query(coord_region, found_points)
		final_neigh=[i+1]
		# Got ID'S OF i'th points Nearesst Neighbours
		# Filter these considering direction,ditance and seq. no.
		for j in range (0,len(found_points)):
			# SELECT ID OF NN POINT OF QUERY POINT
			id = found_points[j]
			# GET ALL METADATA FROM ORIGINAL_DATA FOR THIS NEAREST NEIGHBOUR TO FIYLTER IT  
			# id-1 because numpy array location starts with 0
			longitu = original_data[id-1][1]
			latitu  = original_data[id-1][2]
			diru    = original_data[id-1][3]
			sequ    = original_data[id-1][4]
			# CALCULATE ANGLE CHANGE in ViEW DIRECTION
			anglediff = (original_data[id-1][3]-dir_querypt + 180 + 360) % 360 - 180
			if (anglediff <= 45 and anglediff>=-45):
				# CHECK FOR SEQUENCE NO
				if (sequ!= seq_querypt):
					distance =  points[i].distance_to(points[id-1])
					distanced_neighbours = [distance,id]
					neighs.append(distanced_neighbours)		
		sorted_neighs=sorted(neighs)
		final_neigh+=[x[1] for x in sorted_neighs]		
		querying_nn = time.process_time() - querying_nn_points_t
		# SAVE NN for this coord in DB
		coordinate.neighbors = final_neigh
		coordinate.save()
	query_time = time.process_time() - query_allpoints
	print("\nTOTAL TIME TO FIND NEAREST NEIGHBOUR OF",len(coords),"NEW COORDINATES = ",query_time)

def get_images():
	start = time.time()
	keys = []
	filename =[]
	urls=[]
	# load image keys into variable "[keys]"
	image_keys = Coordinate_property.objects.values_list('image_key', flat=True).exclude(filename__isnull=False)
	for key in image_keys:
			row_entry = key
			keys.append(row_entry)
	# print ("image_name[:10] ",keys)
	# print(type(keys))
	# set resolution
	resolutionA = '/thumb-320.jpg'
	resolutionB = '/thumb-640.jpg'
	resolutionC = '/thumb-1024.jpg'
	resolutionD = '/thumb-2048.jpg'

	# Generate url and file names for all keys
	for i in range (0,len(keys)):
	#for i in range (0,10):
		url = 'https://images.mapillary.com/'
		# formatting image name
		key = str(keys[i]) 
		# build image url for resolutionB '640' 
		url = url + key + resolutionB
		urls.append(url)
	def image_downloader(img_url: str):
		print(f'Downloading: {img_url}')
		res = requests.get(img_url, stream=True)
		count = 1
		while res.status_code != 200 and count <= 5:
			res = requests.get(img_url, stream=True)
			print(f'Retry: {count} {img_url}')
			count += 1
		# checking the type for image
		if 'image' not in res.headers.get("content-type", ''):
			print('ERROR: URL doesnot appear to be an image')
			return False
		# Trying to red image name from response headers
		try:
			image_name = img_url.split("/")
			name = "img_" + str(image_name[3]) + ".jpg"
		except:
			image_name = str(random.randint(11111, 99999))+'.jpg'

		i = Image.open(io.BytesIO(res.content))
		download_location = "./backend/static/Images"
		i.save(download_location + '/'+ name)
		downloaded = Coordinate_property.objects.get(image_key=str(image_name[3]))
		downloaded.filename = "./Images/img_" + str(image_name[3]) + ".jpg"
		downloaded.save()
		return f'Download complete: {img_url}'
	# set number of threads allocated for image_downloader() function
	n_process = 30
	print(f'MESSAGE: Running {n_process} process')
	results = ThreadPool(n_process).imap_unordered(image_downloader, urls)
	for r in results:
		print(r)

	end = time.time()
	print('Time taken to download {}'.format(len(urls)),'images',end - start)

	#Fetches the sequences from Mapillary API 
def sequences():
	regions = Region.objects.all()
	for region in regions:
		print('-------------------------------------------')	
		print('Getting sequences for region: ' + region.name)	
		print('-------------------------------------------')	
		#Mapillary url
		url = 'https://a.mapillary.com/v3/sequences'
		#Set up params to pass in the request 
		client_id = 'dm95M3VFaHJkZ2dDS1RDZzlaVXN1RjpkMDU4NTU5ZDdhMDM4MmZi'
		bbox = str(region.min_longitude) + ','+ str(region.min_latitude) + ',' + str(region.max_longitude) + ',' + str(region.max_latitude)
		if (region.last_update is not None):
			start_time = region.last_update.strftime("%Y-%m-%d")
			PARAMS = {'client_id': client_id, 'bbox': bbox, 'start_time' : start_time}
		else:
			PARAMS = {'client_id': client_id, 'bbox': bbox}
		#Create the request using the params previously defined
		response = requests.get(url, params = PARAMS, headers={'Content-Type': 'application/json'})
		#Get the first url to fetch data
		if (response.status_code == 504):
			if (region.last_update is not None):
				start_time = region.last_update.strftime("%Y-%m-%d")
				PARAMS = {'client_id': client_id, 'bbox': bbox, 'start_time' : start_time}
			else:
				PARAMS = {'client_id': client_id, 'bbox': bbox}
			response = requests.get(url, params = PARAMS, headers={'Content-Type': 'application/json'})	
		url = response.url
		print('-------------------------------------------')	
		print('Getting sequences and points from: ' + url)	
		print('-------------------------------------------')	
		first_run = True 
		counter = 1
		counter_newdata = 0
		counter_newsequence = 0
		while url is not None:	
			if(first_run):			
				response = requests.get(url, headers={'Content-Type': 'application/json'})
				print(str(counter) + ' run')
			else:
				try:
				#Get the next url
					url = response.links["next"]["url"]
					response = requests.get(url, headers={'Content-Type': 'application/json'})
					counter += 1
					print('-------------------------------------------')	
					print('Getting sequences and points from next url: ' + url)
					print(str(counter) + ' run')
					print('-------------------------------------------')
				except:
					break
			first_run = False
			#Get the JSON from the API response
			try:
				imagesFromAPI = json.loads(response.content.decode('utf-8'))
				features = imagesFromAPI['features']	
				#Begin the population of sequences in the DB
				for sequenceLoad in features:			
					camera_makeJ = sequenceLoad['properties']['camera_make']
					captured_atJ = sequenceLoad['properties']['captured_at']
					created_atJ = sequenceLoad['properties']['created_at']
					keyJ = sequenceLoad['properties']['key']
					panoJ = sequenceLoad['properties']['pano']
					user_keyJ = sequenceLoad['properties']['user_key']
					user = User.objects.get(key = user_keyJ)			
					stored_atJ = timezone.now()
					coordinatesJ = sequenceLoad['geometry']['coordinates']		
					casJ = sequenceLoad['properties']['coordinateProperties']['cas']
					image_keysJ = sequenceLoad['properties']['coordinateProperties']['image_keys']
					points_in_seqJ = len(coordinatesJ)
					#only store sequences with more than 15 points
					if points_in_seqJ >= 15:
						print('-------------------------------------------')	
						print('Storing sequence ' + keyJ + ' with ' + str(points_in_seqJ) + ' points.')	
						print('-------------------------------------------')	
						sequenceTostore = Sequence(camera_make = camera_makeJ, captured_at = captured_atJ, created_at = created_atJ,
							key = keyJ, pano = panoJ, user_key = user, region_key = region, stored_at = stored_atJ, points_in_seq = points_in_seqJ)
						try:
							sequenceTostore.save()
							counter_newsequence += 1
							sequenceJ = Sequence.objects.get(key = keyJ)
							#Store the points of the sequence
							for imagetaken, casTaken, coordinatesTaken in zip(image_keysJ, casJ, coordinatesJ):
								caJ = casTaken
								longitudeJ = coordinatesTaken[0]
								latitudeJ = coordinatesTaken[1]
								image_keyJ = imagetaken										
								one = Coordinate_property(ca = caJ, image_key = image_keyJ, longitude = longitudeJ, latitude = latitudeJ,
									sequence_key = sequenceJ)
								one.save()						
								counter_newdata += 1
							#Calculate the direction for all the points in the sequence
							getdirection(sequenceTostore)
							print('-------------------------------------------')	
							print('Calculated direction for sequence: ' + sequenceTostore.key)	
							print('-------------------------------------------')	
						except IntegrityError: 
							continue
				finishedcorrectly = True
			except ValueError: 
				print ('Decoding JSON has failed')
				finishedcorrectly = False
		#Calculate the neighbors for the new points in the DB
		#deltaneighbors()
		if (finishedcorrectly):
			region.last_update = timezone.now()
			region.save()
		print(str(counter_newsequence) + ' new sequences had been stored.')  
		print(str(counter_newdata) + ' new points had been stored.')  

	#Calculate the direction for all the coordinates in the database
def sanitydirection():
	allsequences = Sequence.objects.all().order_by('id')
	for sequence in allsequences:
		firstcoord = Coordinate_property.objects.filter(sequence_key = sequence.id).first()
		if(firstcoord.direction is None):
			getdirection(sequence)
			print('-------------------------------------------')	
			print('Calculated direction for sequence: ' + sequence.key)	
			print('-------------------------------------------')	

	#Function called by calculatealldirection, calculate the direction for a particular sequence
def getdirection(sequencetosearch):
	coordinates = Coordinate_property.objects.filter(sequence_key = sequencetosearch.id).order_by('id')
	lastcoordinate = Coordinate_property.objects.filter(sequence_key = sequencetosearch.id).order_by('id').last()
	previousdirection = 0
	#LOOP THROUGH THE COORDINATES FROM THE SEQUENCE
	for coordinate in coordinates:
		#CASE LAST COORDINATE FROM THE PARTICULAR SEQUENCE
		if coordinate == lastcoordinate:
			coordinate.direction = previousdirection
		#OTHER CASES  
		else:
			lat1 = coordinate.latitude
			long1 = coordinate.longitude        
			nextcoordinate = Coordinate_property.objects.filter(id__gt = coordinate.id).order_by('id').first()
			lat2 = nextcoordinate.latitude
			long2 = nextcoordinate.longitude
			coordinate.direction = angleFromCoordinateLib(lat1, long1, lat2, long2)
			if(coordinate.direction == 0):
				coordinate.direction = previousdirection
			previousdirection = coordinate.direction
		coordinate.save()
 
 #Fetch all the users for a region from Mapillary
def users():
	regions = Region.objects.all()
	for region in regions:
		print('-------------------------------------------')	
		print('Getting users for region: ' + region.name)	
		print('-------------------------------------------')	
		url = 'https://a.mapillary.com/v3/users'
		client_id = 'dm95M3VFaHJkZ2dDS1RDZzlaVXN1RjpkMDU4NTU5ZDdhMDM4MmZi'
		bbox = str(region.min_longitude) + ','+ str(region.min_latitude) + ',' + str(region.max_longitude) + ',' + str(region.max_latitude)
		if (region.last_update is not None):
			start_time = region.last_update.strftime("%Y-%m-%d")	
			print('-------------------------------------------')	
			print('Last update of the region: ' + start_time)	
			print('-------------------------------------------')
			PARAMS = {'client_id': client_id, 'bbox': bbox, 'start_time' : start_time}
		else:
			print('-------------------------------------------')	
			print('First time fetching information for this region')	
			print('-------------------------------------------')
			PARAMS = {'client_id': client_id, 'bbox': bbox}
		response = requests.get(url, params = PARAMS, headers={'Content-Type': 'application/json'}) 
		url = response.links["first"]["url"]
		print('-------------------------------------------')	
		print('Getting users from: ' + url)	
		print('-------------------------------------------')	
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
				try:          
					one = User(about = aboutJ, avatar = avatarJ, created_at = created_atJ, key = keyJ,
						username = usernameJ, stored_at = stored_atJ)
					one.save()
					counter_newdata += 1
				except IntegrityError: 
					continue  
		print('-------------------------------------------')	
		print(str(counter_newdata) + ' new users stored.')
		print('-------------------------------------------')  

