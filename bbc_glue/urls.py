from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('home_1/', views.home_1, name='home_1'),
    path('home_2/', views.home_2, name='home_2'),
    path('home_3/', views.home_3, name='home_3'),
    path('home_4/', views.home_4, name='home_4'),
    # path('home_5/', views.home_5, name='home_5'),
    # path('home_6/', views.home_6, name='home_6'),
]