# disk_management/urls.py
from django.urls import path
from . import views

app_name = 'disk_management'

urlpatterns = [
    path('', views.index, name='index'),
]