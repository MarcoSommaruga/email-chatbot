import os
import base64
import datetime
from email import message_from_bytes
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Carica le variabili d'ambiente dal file .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Scopo per leggere le email
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File token
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

# Crea il file credentials.json dinamicamente se non esiste
if not os.path.exists(CREDENTIALS_FILE):
    credentials_data = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    import json
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials_data, f)

# Autenticazione OAuth2
def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080, host='127.0.0.1')
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

# Estrai mittente, oggetto e corpo da un messaggio Gmail
def parse_email(msg):
    headers = msg['payload'].get('headers', [])
    subject = sender = ""
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'From':
            sender = header['value']
    body = ""
    parts = msg['payload'].get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return {"from": sender, "subject": subject, "body": body}

# Scarica email dalle ultime 24 ore
def fetch_recent_emails():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    now = datetime.datetime.utcnow()
    yesterday = now - datetime.timedelta(days=1)
    query = f"after:{int(yesterday.timestamp())}"
    results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        parsed = parse_email(msg_data)
        emails.append(parsed)
    return emails

# Salva le email in un file JSON
def save_emails_to_json(emails, filename="emails.json"):
    import json
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(emails, f, ensure_ascii=False, indent=4)

# Esegui il download e stampa le email
if __name__ == "__main__":
    emails = fetch_recent_emails()
    save_emails_to_json(emails)
    for i, email in enumerate(emails, 1):
        print(f"\n📧 Email {i}")
        print(f"Da: {email['from']}")
        print(f"Oggetto: {email['subject']}")
        print(f"Corpo:\n{email['body']}")