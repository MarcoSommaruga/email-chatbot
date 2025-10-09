import sys
sys.path.insert(1, './log/src')
from log_utils import LogManager

# Inizializza il logger per il main
logger = LogManager(__name__, "./log/logs/main.log").get_logger()

def main():
    logger.info("Avvio modulo search: similarità query-emails.")

    try:
        # Importa ed esegue il modulo search (che ha il proprio main())
        from search import main as search_main
        logger.info("Chiamata al modulo di ricerca.")
        search_main()
    except Exception as e:
        logger.exception("Errore nell'esecuzione dell'applicazione principale: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()