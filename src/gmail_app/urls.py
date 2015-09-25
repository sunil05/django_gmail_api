"""gmail_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import os
from django.conf.urls import include, url
from django.contrib import admin
import mails.urls
import registration.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authorize_app/$', 'user_credentials.views.index'),
    url(r'^authorize_app/oauth2callback', 'user_credentials.views.auth_return'),
    url(r'^search_box/', include(mails.urls)),
    url(r'^accounts/', include(registration.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
]
