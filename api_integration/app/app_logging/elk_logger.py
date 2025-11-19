import logging
import json
import socket
from logging.handlers import HTTPHandler
from app.config import ELK_HOST, ELK_PORT, ELK_INDEX, SERVICE_NAME

class ELKHTTPHandler(HTTPHandler):
    """
    Handler personnalisé pour envoyer des logs structurés JSON vers Logstash/ELK via HTTP.
    """

    def mapLogRecord(self, record):
        """
        Convertit un LogRecord en dict JSON.
        """
        log_entry = {
            "service": SERVICE_NAME,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "hostname": socket.gethostname()
        }
        # Si record.msg est un dict, l'ajouter directement
        if isinstance(record.msg, dict):
            log_entry.update(record.msg)
        # Retourner un dict (HTTPHandler s'attend à un mapping pour urlencode)
        return log_entry

# --- Création du logger global
logger = logging.getLogger("elk_logger")
logger.setLevel(logging.INFO)

# Handler HTTP vers Logstash/Elasticsearch
elk_handler = ELKHTTPHandler(
    host=f"{ELK_HOST}:{ELK_PORT}",
    url=f"/{ELK_INDEX}/_doc",
    method="POST"
)

logger.addHandler(elk_handler)

# --- Exemples d'utilisation
if __name__ == "__main__":
    logger.info({"event": "test_log", "message": "Ceci est un test de log ELK"})
    logger.error({"event": "test_error", "message": "Erreur simulée"})
