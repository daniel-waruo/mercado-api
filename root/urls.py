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
from django.http import HttpResponse
from django.urls import path
from ussd.views import ussd_bot
from whatsapp.utils import send_whatsapp
from whatsapp.views import whatsapp_bot, whatsapp_bot_status
from orders.views import confirm_payment
from django.views.decorators.csrf import csrf_exempt

admin.site.site_header = 'Leta Gas Admin'
admin.site.index_title = 'Site Administration'
admin.site.site_title = 'Leta Gas Admin'

urlpatterns = [
    path('whatsapp-bot/status', whatsapp_bot_status, name='whatsapp-status'),
    path('whatsapp-bot', whatsapp_bot, name='whatsapp-bot'),

    path('ussd-bot', csrf_exempt(ussd_bot), name='gas-bot'),
    path('ussd/checkout_callback', confirm_payment, name='gas-callback'),

    path('', admin.site.urls),
]
