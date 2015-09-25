import os
from django.conf.urls import include, url

urlpatterns = [
    url(r'home.html', 'mails.views.home'),
    url(r'', 'mails.views.search_box'),
]
