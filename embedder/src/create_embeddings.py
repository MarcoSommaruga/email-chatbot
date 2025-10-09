import logging
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/logs/create_embeddings.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    # Inizializza il modello
    logger.info("Inizializzazione del modello SentenceTransformer.")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Carica la lista di email
    logger.info("Caricamento email da file.")
    with open("./data/emails.json", "r", encoding="utf-8") as f:
        email_texts = json.load(f)

    # Estrai i corpi delle email 
    logger.info("Estrazione dei corpi delle email.")
    email_bodies = []
    for email in email_texts:
        body = email.get("body", "")
        if body:
            email_bodies.append(body)
        else:
            pass
            logger.warning("Email senza corpo trovato: %s", email)

    if not email_bodies:
        logger.error("Nessun corpo email trovato per l'encoding.")
        exit(1)

    # Calcola gli embedding
    logger.info("Calcolo degli embedding.")
    email_embeddings = model.encode(email_bodies, convert_to_numpy=True)

    # Salva gli embedding per uso futuro
    np.save("./data/email_embeddings.npy", email_embeddings)
    logger.info("Embedding salvati in ./data/email_embeddings.npy.")

    # Salva anche i testi associati (opzionale)
    with open("./data/email_texts.txt", "w", encoding="utf-8") as f:
        for email in email_bodies:
            f.write(email + "\n")
    logger.info("Testi delle email salvati in ./data/email_texts.txt.")

    logger.info("Embedding creati e salvati con successo.")
except Exception as e:
    logger.exception("Errore durante la creazione degli embedding: %s", e)