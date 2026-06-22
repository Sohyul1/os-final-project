# memory_management/urls.py
from django.urls import path
from . import views

app_name = 'memory_management'

urlpatterns = [
    path('', views.index, name='index'),
]