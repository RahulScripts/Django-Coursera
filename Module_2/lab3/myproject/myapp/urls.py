from django.urls import path
from . import views

urlpatterns = [
    path('<str:drink_name>/', views.drinks, name="drink_name"), 
]