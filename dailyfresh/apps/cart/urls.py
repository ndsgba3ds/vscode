from django.contrib import admin
from django.urls import path, include
from cart.views import CartAddView, CartInfoView

urlpatterns = [
    path('add', CartAddView.as_view(), name='add'),
    path('',CartInfoView.as_view(),name='show')
]
