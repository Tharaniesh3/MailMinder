import time
from flask import Flask, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openai
from flask_caching import Cache
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# OpenAI API credentials
OPENAI_API_KEY = ""
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def list_inbox_emails(service, batch_size, max_emails):
    emails = []
    try:
        page_token = None
        index = 1  # Index for each email
        while len(emails) < max_emails:  # Stop when the desired number of emails is reached
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
        return emails[:max_emails]  # Return only the first 50 emails

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


@app.route('/emails', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_emails():
    creds = cache.get('credentials')
    if not creds:
        # Get the absolute path of the credentials.json file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(current_dir, 'credentials.json')
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        cache.set('credentials', creds)
    elif creds.expired:
        creds.refresh(Request())

    try:
        service = build('gmail', 'v1', credentials=creds)
        batch_size = 10
        max_emails = 50
        emails = list_inbox_emails(service, batch_size, max_emails)

        for email in emails:
            summary = summarize_text(email['subject'], email['snippet'])
            email['summary'] = summary
        return jsonify(emails)

    except HttpError as error:
        return jsonify({'error': f'An error occurred: {error}'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
