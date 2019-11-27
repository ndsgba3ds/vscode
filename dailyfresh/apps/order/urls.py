from django.contrib import admin
from django.urls import path, include
from order.views import OrderPlaceView, OrderCommitView, OrderCheckView, OrderPayView

urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'),
    path('commit', OrderCommitView.as_view(), name='commit'),
    path('pay', OrderPayView.as_view(), name='pay'),
    path('check', OrderCheckView.as_view(), name='pay')
]
