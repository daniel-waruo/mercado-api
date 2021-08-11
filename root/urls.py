"""root URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from ussd.views import index
from orders.views import confirm_payment

admin.site.site_header = 'Leta Gas Admin'
admin.site.index_title = 'Site Administration'
admin.site.site_title = 'Leta Gas Admin'

urlpatterns = [
    path('', admin.site.urls),
    path('ussd/', index),
    path('ussd/checkout_callback', confirm_payment)
]
