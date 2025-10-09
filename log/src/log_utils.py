import logging

class LogManager:
    def __init__(self, name=__name__, log_file="app.log"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            # Handler per file
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            # Handler per console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            # Formatter
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            # Aggiunge gli handler
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger