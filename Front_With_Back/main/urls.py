from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path('login/', views.loginCastom, name='login'),
    path('logout/', views.logoutCastom, name='logout'),
    path('register/', views.register, name='register'),
    path('main_page/', views.home, name='mainp'),
    path('new_pas/', views.home, name='new_pas'), # -
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)