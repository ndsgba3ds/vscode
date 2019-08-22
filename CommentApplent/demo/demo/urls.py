"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from api import views
from demo.settings import MEDIA_ROOT
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('admin/', admin.site.urls),
    path('api/wx_login',views.wx_login),
    path('api/get_employees',views.get_employees),
    path('api/get_employee_by_id',views.get_employee_by_id),
    path('api/add_comment',views.add_comment),
    # path('media/(<str:path>.*)', serve, {"document_root": MEDIA_ROOT})
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT})
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
