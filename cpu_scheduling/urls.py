
from django.urls import path
from . import views

app_name = 'cpu_scheduling'

urlpatterns = [
    path('', views.index, name='index'),
]