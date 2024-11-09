import base64
import google.auth
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Replace with your service account credentials file path
SERVICE_ACCOUNT_FILE = 'docs/novahacksproject-dc5e2e740f31.json'

# Authenticate using service account credentials
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build('gmail', 'v1', credentials=creds)

# List messages in the inbox
results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
messages = results.get('messages', [])

# Get the first message
message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()

# Print the message's subject and sender
print(message['snippet'])
print(message['payload']['headers'][0]['value'])

# Send a new email
message = {
    'to': 'aarushaga@gmail.com',
    'from': 'aarusha@andrew.cmu.edu',
    'subject': 'Hello from the Gmail API',
    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
}

result = service.users().messages().send(userId='me', body=message).execute()