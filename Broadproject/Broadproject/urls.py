"""
URL configuration for Broadproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path,include
from usersection import urls
from restaurant import urls
from adminsection import urls,views
from foodsection import urls
from jobsection import urls
from jobadmin import urls
from doctorAdmin import urls
from doctorSection import urls
from . import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.adminlogin,name="adminlogin"),
    path('user/',include('usersection.urls')),
    path('restaurant/',include('restaurant.urls')),
    path('food/',include('foodsection.urls')),
    path('adminsection/',include('adminsection.urls')),
    path('job/',include('jobsection.urls')),
    path('jobadmin/',include('jobadmin.urls')),
    path('doctorAdmin/',include('doctorAdmin.urls')),
    path('doctorSection/',include('doctorSection.urls')),
    path('buysellAdmin/',include('buysellAdmin.urls')),
    path('buysellSection/', include('buysellSection.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
