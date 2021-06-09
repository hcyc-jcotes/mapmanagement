# from django.urls import path
# from . import views
# from django.views.generic import TemplateView

# urlpatterns = [
#     path('', views.home, name='home'),  #  on the frontend when django searches for 
#                                         # 'http://127.0.0.1:8000/' lands here, it loads the view from views         
#     path('response', views.response, name='response'),
#     path('users', views.users, name='users'),   
#     path('sequences', views.sequences, name='sequences'),     
#     path('neighbors', views.neighbors, name='neighbors'),
#     path('downloadimages', views.downloadimages, name='downloadimages'),
#     path('calculatealldirection', views.calculatealldirection, name='calculatealldirection'),
#     path('deltaneighbors', views.deltaneighbors, name='deltaneighbors'),
#     path('api/coordinates/', views.CoordinatePropertyView.as_view()),
#     path('api/regions/', views.RegionView.as_view()),
#     path('api/sequences/', views.SequenceView.as_view()),                                                            
#     #path('', views.home, name='home'),  #  on the frontend when django searches for 
#                                         # 'http://127.0.0.1:8000/' lands here, it loads the view from views
#     #path('', TemplateView.as_view(template_name='index.html')),
# ]