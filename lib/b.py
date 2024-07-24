from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import openai

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# OpenAI API credentials
OPENAI_API_KEY = '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'

def list_inbox_emails(service, batch_size):
    emails = []
    try:
        page_token = None
        index = 1  # Index for each email
        while True:
            response = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=batch_size, pageToken=page_token).execute()
            messages = response.get('messages', [])
            if not messages:
                break
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                subject = None
                sender = None
                date = None
                snippet = msg['snippet']
                for header in headers:
                    name = header['name']
                    if name.lower() == 'subject':
                        subject = header['value']
                    elif name.lower() == 'from':
                        sender = header['value']
                    elif name.lower() == 'date':
                        date = header['value']
                email = {
                    'index': index,  # Add index for each email
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet
                }
                emails.append(email)
                index += 1  # Increment the index
            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break
        return emails
    except HttpError as error:
        print(f'An error occurred: {error}')
        return emails


def summarize_text(subject, text):
    openai.api_key = OPENAI_API_KEY
    prompt = f"Subject: {subject}\nSnippet: {text}\n\nSummarize:"
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


def get_emails():
    creds = None 
    creds = service_account.Credentials.from_service_account_file('lib/credentials.json', scopes=SCOPES)
    try:
        service = build('gmail', 'v1', credentials=creds)
        batch_size = 30
        emails = list_inbox_emails(service, batch_size)
        for email in emails:
            summary = summarize_text(email['subject'], email['snippet'])
            email['summary'] = summary
        return emails

    except HttpError as error:
        return {'error': f'An error occurred: {error}'}

email_data = get_emails()
print(email_data)

