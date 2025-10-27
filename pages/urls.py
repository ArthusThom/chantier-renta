from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('estimation/', views.estimation, name='estimation'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
    path('send-email/', views.send_email, name='send_email'),
]
