import os
import json
import base64
import datetime
import logging
from email import message_from_bytes
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configurazione del logger con differenziazione dei livelli
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("fetch_emails.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def raiseException(e, msg=""):
    # Uso di critical per errori da cui non ci si può recuperare
    logger.critical(msg, exc_info=True)
    raise e

# Carica le variabili d'ambiente dal file .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raiseException(Exception("Missing environment variables"),
                   "Variabili d'ambiente mancanti: CLIENT_ID, CLIENT_SECRET e/o REDIRECT_URI")

# Scopo per leggere le email
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File token e credentials
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
    try:
        with open(CREDENTIALS_FILE, 'w', encoding="utf-8") as f:
            json.dump(credentials_data, f, indent=4)
        logger.info("Creato il file credentials.json dinamicamente")
    except Exception as e:
        raiseException(e, "Errore nella creazione di credentials.json")

# Autenticazione OAuth2
def authenticate_gmail():
    creds = None
    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logger.info("Token letto da file")
    except Exception as e:
        raiseException(e, f"Errore durante la lettura di {TOKEN_FILE}")
    
    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info("Token aggiornato con successo")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080, host='127.0.0.1')
                logger.info("Autenticazione completata tramite browser")
            with open(TOKEN_FILE, 'w', encoding="utf-8") as token:
                token.write(creds.to_json())
                logger.info("Token salvato su file")
    except Exception as e:
        raiseException(e, "Errore nell'autenticazione")
    return creds

# Estrai mittente, oggetto e corpo da un messaggio Gmail
def parse_email(msg):
    try:
        headers = msg['payload'].get('headers', [])
        subject = sender = ""
        for header in headers:
            if header.get('name') == 'Subject':
                subject = header.get('value', '')
            elif header.get('name') == 'From':
                sender = header.get('value', '')
        body = ""
        parts = msg['payload'].get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return {"from": sender, "subject": subject, "body": body}
    except Exception as e:
        # Uso error per errori nel parsing, ma se possibile si continua
        logger.error("Errore nel parsing dell'email: %s", e, exc_info=True)
        return {"from": "", "subject": "", "body": ""}

# Scarica email dalle ultime 24 ore
def fetch_recent_emails():
    emails = []
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)
        now = datetime.datetime.utcnow()
        yesterday = now - datetime.timedelta(days=1)
        query = f"after:{int(yesterday.timestamp())}"
        results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
        messages = results.get('messages', [])
        logger.info("Trovati %d messaggi", len(messages))
        for msg in messages:
            try:
                msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
                parsed = parse_email(msg_data)
                emails.append(parsed)
            except Exception as e:
                logger.warning("Errore nel recupero o parsing del messaggio con ID %s: %s", msg['id'], e, exc_info=True)
        return emails
    except Exception as e:
        raiseException(e, "Errore durante il recupero delle email")

# Salva le email in un file JSON
def save_emails_to_json(emails, filename="emails.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(emails, f, ensure_ascii=False, indent=4)
        logger.info("Email salvate su %s", filename)
    except Exception as e:
        raiseException(e, "Errore nel salvataggio delle email")

if __name__ == "__main__":
    try:
        emails = fetch_recent_emails()
        if emails:
            save_emails_to_json(emails)
            for i, email in enumerate(emails, 1):
                print(f"\n📧 Email {i}")
                print(f"Da: {email['from']}")
                print(f"Oggetto: {email['subject']}")
                print(f"Corpo:\n{email['body']}")
        else:
            logger.warning("Nessuna email recuperata.")
    except Exception as main_e:
        raiseException(main_e, "Errore critico nell'esecuzione dello script")