from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'webhook'

urlpatterns = [
    path('endpoint/', views.endpoint, name='endpoint'),
]
