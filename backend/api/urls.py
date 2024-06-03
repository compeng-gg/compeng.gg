from . import views

from django.urls import path

app_name = 'api'

urlpatterns = [
    path('auth/login/', views.login),
    path('auth/logout/', views.logout),
]
