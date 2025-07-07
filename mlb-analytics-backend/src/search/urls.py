from django.urls import path
from . import views

urlpatterns = [
    path('natural/', views.natural_language_search, name='natural_language_search'),
]
