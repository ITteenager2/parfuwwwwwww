from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def get_google_docs_content(doc_id):
    """Gets the content of a Google Doc by its ID."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=doc_id).execute()
        
        content = ''
        for elem in document.get('body').get('content'):
            if 'paragraph' in elem:
                for paraPart in elem.get('paragraph').get('elements'):
                    if 'textRun' in paraPart:
                        content += paraPart.get('textRun').get('content')
        
        return content
    except Exception as e:
        print(f"Error accessing Google Doc: {e}")
        return None

