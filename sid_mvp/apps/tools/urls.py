# apps/tools/urls.py
from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tools/', views.tool_list, name='tool_list'),
    path('tools/create/', views.tool_create, name='tool_create'),
    path('tools/<int:pk>/', views.tool_detail, name='tool_detail'),
    path('tools/<int:pk>/edit/', views.tool_edit, name='tool_edit'),
    path('tools/<int:pk>/operate/', views.tool_operation, name='tool_operation'),
    path('tools/<int:pk>/write_off/', views.tool_write_off, name='tool_write_off'),  # ← НОВОЕ
    path('tools/<int:pk>/qr/', views.qr_print, name='qr_print'),
]