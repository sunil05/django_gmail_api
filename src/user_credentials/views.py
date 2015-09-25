# Create your views here.
import os
import logging
import httplib2

from django.contrib.auth.models import User
from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from user_credentials.models import CredentialsModel
from gmail_app import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENTSECRETS_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')
REDIRECT_URI = 'http://localhost:8000/authorize_app/oauth2callback/'
SCOPES = [
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          # Add other requested scopes.
]

FLOW = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, SCOPES, REDIRECT_URI)

def get_credential(user):
    storage = Storage(CredentialsModel, 'user', user, 'credential')
    credential = storage.get()
    return credential
 
def build_service(credentials):
  """Build a Gmail service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Gmail service object.
  """
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('gmail', 'v1', http=http)

@login_required
def index(request):
    storage = Storage(CredentialsModel, 'user', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['access_type'] = 'offline'
        FLOW.params['approval_prompt'] = 'force'
        usr = User.objects.get(username=request.user)
        FLOW.params['user_id'] = usr.email
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        return HttpResponseRedirect("/search_box/home.html")

@login_required
def auth_return(request):
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'user', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("/authorize_app/")
