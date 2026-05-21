from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start, name='start'),
    path('question/', views.question, name='question'),
    path('results/', views.results, name='results'),
    path('history/', views.history, name='history'),
]
