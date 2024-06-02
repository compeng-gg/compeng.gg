from django.urls import path

from . import views

urlpatterns = [
    path("", views.lab5, name="lab5"),
]
