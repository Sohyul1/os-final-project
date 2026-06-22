# virtual_memory/urls.py
from django.urls import path
from . import views

app_name = 'virtual_memory'

urlpatterns = [
    path('', views.index, name='index'),
]