from django.contrib import admin
from django.urls import path, include
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 注册
    path('activate/<str:token>', ActiveView.as_view(), name='active'),  # 激活
    path('login', LoginView.as_view(), name='login'),  # 登录
    path('logout', LogoutView.as_view(), name='logout'),
    path('', UserInfoView.as_view(), name='center'),
    path('order/<int:page>/', UserOrderView.as_view(), name='order'),
    path('address', AddressView.as_view(), name='address')
]
