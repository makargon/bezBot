from .import views
from django.urls import path

urlpatterns = [
    path('event/', views.event_log),
]