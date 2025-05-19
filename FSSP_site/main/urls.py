from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginCastom, name='login'),
    path('logout/', views.logoutCastom, name='logout'),
    path('register/', views.register, name='register'),
    path('accounts/profile/', views.home, name='home'),
]