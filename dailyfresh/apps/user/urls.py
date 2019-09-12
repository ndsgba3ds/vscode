from django.contrib import admin
from django.urls import path, include
from user.views import RegisterView, ActiveView, LoginView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 注册
    path('activate/<str:token>', ActiveView.as_view(), name='active'),  # 激活
    path('login', LoginView.as_view(), name='login')  # 登录
]
