import sys
sys.path.insert(1, './log/src')
from log_utils import LogManager

# Inizializza il logger per il main
logger = LogManager(__name__, "./log/logs/main.log").get_logger()

def main():
    logger.info("Avvio modulo fetch_emails: recupero mail.")

    try:
        # Importa ed esegue il modulo fetch_emails (che ha il proprio main())
        from fetch_emails import main as fetch_emails_main
        logger.info("Chiamata al modulo di fetch delle email.")
        fetch_emails_main()
    except Exception as e:
        logger.exception("Errore nell'esecuzione dell'applicazione principale: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()