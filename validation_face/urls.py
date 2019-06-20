# from rest_framework.routers import SimpleRouter
#
# from recognition_opencv.views import *
#
# router = SimpleRouter()
#
# router.register('recognition_opencv', recognitionViewSet, base_name='recognition')

from django.contrib import admin
from django.urls import path

from validation_face import views

urlpatterns = [
    path('recognize/', views.recognize_image)
]