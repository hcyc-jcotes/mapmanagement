"""
FOR MILESTONE 1 - TEAM 03

URLS used by the backend
"""
from django.contrib import admin
from django.urls import include, path
from backend import views
from backend import api_views

urlpatterns = [
	# path('', include('backend.urls')), #home path says if you land at 'http://127.0.0.1:8000/' take you to frontend
	path('', include('frontend.urls')),
	path('admin/', admin.site.urls),
	# path('backend', views.home, name='backend'),
	path('response', views.response, name='response'),
	path('users', views.users, name='users'),   
	path('sequences', views.sequences, name='sequences'),     
	path('neighbors', views.neighbors, name='neighbors'),
	path('sanitydirection', views.sanitydirection, name='sanitydirection'),
	#path('mapillaryupdate', views.mapillaryupdate, name='mapillaryupdate'),
	path('deltaneighbors', views.deltaneighbors, name='deltaneighbors'),
	# path('index', views.index, name='index'),
	path('api/coordinates/', api_views.CoordinatePropertyView.as_view()),
	path('api/regions/', api_views.RegionView.as_view()),
	path('api/sequences/', api_views.SequenceView.as_view()), 
]

import time

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from backend.views import users, sequences, neighbors, deltaneighbors, sanitydirection,get_images
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "defaultjob")

@register_job(scheduler, "interval", weeks = 2)
def mapillaryupdate():
	print('-------------------------------------------')	
	print('Updating function - fetching users from Mapillary')	
	print('-------------------------------------------')	
	users()
	print('-------------------------------------------')	
	print('Updating function - fetching sequences from Mapillary')	
	print('-------------------------------------------')	
	sequences()
	print('-------------------------------------------')	
	print('Updating function - Checking directions for all data')	
	print('-------------------------------------------')	
	sanitydirection()
	print('-------------------------------------------')	
	print('Updating function - Calculating neighbors')	
	print('-------------------------------------------')
	deltaneighbors()
	print('-------------------------------------------')	
	print('Downloading images')	
	print('-------------------------------------------')
	get_images()
	print('-------------------------------------------')	
	print('Finished Fetching')	
	print('-------------------------------------------')

register_events(scheduler)

scheduler.start()
print("Scheduler started!")