from django.shortcuts import render_to_response
import base64
import email
from django.contrib.auth.decorators import login_required
from user_credentials.views import get_credential, build_service
from apiclient import errors

# Create your views here.
@login_required
def home(request):
    return render_to_response('home.html', {})

def search_box(request):
    credential = get_credential(request.user)
    service = build_service(credential)
    mails = ListMessagesMatchingQuery(service, request.GET.get('query'))
    return render_to_response('home.html', {'mails': mails})

def ListMessagesMatchingQuery(service, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId='me',
                                                     q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                                               pageToken=page_token).execute()
            messages.extend(response['messages'])
        
        message_list = []
        for msg_dict in messages:
            message_list.append(GetMessage(service, msg_dict['id']))
        return message_list 
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def GetMessage(service, msg_id):
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)
        return get_first_text_part(mime_msg)
        #from email.parser import Parser
        #headers = Parser().parsestr(msg_str)
        #return str(msg_str).replace('\r\n', '<p>')
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def get_first_text_part(msg):
    maintype = msg.get_content_maintype()
    if maintype == 'multipart':
        for part in msg.get_payload():
            mime_type = part.get_content_maintype()
            if mime_type == 'text' or mime_type == 'html':
                return part.get_payload()
            else: 
                return get_first_text_part(part)
    elif maintype == 'text':
        return msg.get_payload()
