from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "queue"

urlpatterns = [
    path("", views.webhook, name="webhook"),
]
