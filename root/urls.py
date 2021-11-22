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
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from orders.views import confirm_payment
from ussd.views import ussd_bot_gas,ussd_bot_eggs
from whatsapp.views import whatsapp_bot

admin.site.site_header = 'Leta Gas Admin'
admin.site.index_title = 'Site Administration'
admin.site.site_title = 'Leta Gas Admin'

urlpatterns = [
    path('whatsapp-bot', whatsapp_bot, name='whatsapp-bot'),
    path('ussd-bot/gas', csrf_exempt(ussd_bot_gas), name='gas-bot'),
    path('ussd-bot/eggs', csrf_exempt(ussd_bot_eggs), name='eggs-bot'),
    path('ussd/checkout_callback', confirm_payment, name='gas-callback'),
    path('api/', include('api.urls')),
    path('admin', admin.site.urls),
]
