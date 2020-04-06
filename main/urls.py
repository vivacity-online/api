from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('home', views.HomeView.as_view(), name="home"),
]
