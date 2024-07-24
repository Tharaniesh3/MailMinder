from flask import Flask, jsonify
from flask_caching import Cache
import os
import lib.gmaik.gmail_api as gmail_api
import summarization

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def list_inbox_emails(service, batch_size):
    # Your original implementation of fetching emails
    # ... (include the list_inbox_emails function here)
    @app.route('/emails', methods=['GET'])
    @cache.cached(timeout=60)  # Cache the response for 60 seconds
    def get_emails():
        service = gmail_api.get_gmail_service()
        if not service:
            return jsonify({'error': 'Gmail authentication failed'})

    batch_size = 30
    emails = list_inbox_emails(service, batch_size)
    for email in emails:
        summary = summarization.summarize_text(email['subject'], email['snippet'])
        email['summary'] = summary
    return jsonify(emails)

if __name__ == '__main__':
    app.run(port = 5000,debug=True)
