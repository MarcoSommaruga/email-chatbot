from sentence_transformers import SentenceTransformer, util
import numpy as np
import sys
import json
sys.path.insert(1, './log/src')
from log_utils import LogManager

logger = LogManager(__name__, "./log/logs/search.log").get_logger()

def main():
    try:
        logger.info("Inizializzazione del modello SentenceTransformer.")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        logger.info("Caricamento degli embeddings delle email da file.")
        emails_embeddings = np.load("./data/email_embeddings.npy")
        logger.info("Embeddings caricati correttamente.")

        ## Esempio di query
        query = "ordine amazon per sigaretta elettronica"
        logger.info("Calcolo embedding per la query: %s", query)

        query_embedding = model.encode(query, convert_to_numpy=True)
        logger.info("Embedding della query calcolato con successo.")

        # Calcolo della similarità tra la query e gli embeddings delle email
        logger.info("Calcolo della similarità coseno tra query e embeddings delle email.")
        cosine_scores = util.cos_sim(query_embedding, emails_embeddings)
        logger.info("Calcolo della similarità completato.")

        logger.info("Visualizzazione dei risultati.")
        print('Email più simile: ', np.argmax(cosine_scores[0][:]))
        print('Similarità: ', np.max(np.array(cosine_scores[0])))
        with open("./data/emails.json", "r", encoding="utf-8") as f:
            emails = json.load(f)
        print('Testo email più simile: ', emails[np.argmax(cosine_scores[0][:])]["body"])
        #for i in range(len(emails_embeddings)):
        #    logger.info("Email %d: Similarità: %.4f", i, cosine_scores[0][i])
        #    # Puoi abilitare i print se necessario:
        #     print(f"Email: {emails_embeddings[i]}")
        #     print(f"Similarità: {cosine_scores[0][i]:.4f}")
        #     print()
            
    except Exception as e:
        logger.exception("Errore durante l'esecuzione dello script di ricerca: %s", e)

if __name__ == "__main__":
    main()