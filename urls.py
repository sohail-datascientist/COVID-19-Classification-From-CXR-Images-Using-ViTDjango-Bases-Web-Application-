from django.contrib import admin
from django.urls import path
from . import views
from predictor.views import index, register, login_user, home,dashboard, logout_user

urlpatterns = [
    # path('dash/', views.dashboard),
    path('signup/',register),
    path('',home),
    path('login/',login_user),
    path ('dashboard/', dashboard),
    path('classify/', views.index),
    path('logout_user/', logout_user),
    path('admin/', admin.site.urls),
]