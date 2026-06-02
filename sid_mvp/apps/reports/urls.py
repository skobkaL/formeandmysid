from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.simple_report, name='simple'),
]