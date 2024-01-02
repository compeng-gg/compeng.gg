from django.urls import path

from . import views

urlpatterns = [
    path("join/<str:role>/", views.join, name='join'),
]
