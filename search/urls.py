from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('suggest/', views.suggest, name='suggest'),
    path('search/', views.search, name='search'),
]