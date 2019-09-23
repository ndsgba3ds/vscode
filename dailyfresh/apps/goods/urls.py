from django.contrib import admin
from django.urls import path, include
from goods.views import IndexView, DetailView, ListView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('goods/<int:goods_id>', DetailView.as_view(), name='detail'),
    path('list/<int:type_id>/<int:page>/', ListView.as_view(), name='list')
]
