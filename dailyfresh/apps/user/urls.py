from django.contrib import admin
from django.urls import path, include
from user.views import RegisterView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register')  # 注册
]