from django.urls import path
from django.views.generic import TemplateView

app_name = "docs"

urlpatterns = [
    path("", TemplateView.as_view(template_name="docs/index.html"),
         name="index"),
]
