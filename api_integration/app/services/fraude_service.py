from app.models.fraude_model import fraude_model
from app.config import FRAUDE_ALERT_THRESHOLD
from app.logging.elk_logger import logger

class FraudeService:
    """
    Service de détection de fraude :
    - Prétraitement des données
    - Application des règles métier
    - Appel du modèle ML
    - Post-traitement et génération d'alerte
    """

    def preprocess(self, transaction: dict) -> dict:
        """
        Prétraitement des données transactionnelles.
        Exemple : normalisation, ajout de features dérivées.
        """
        processed = transaction.copy()
        # Feature dérivée : montant / 1000
        processed["montant_k"] = processed.get("montant", 0) / 1000
        # Cap sur historique impayé
        processed["historique_impaye"] = min(processed.get("historique_impaye", 0), 10)
        return processed

    def postprocess(self, result: dict) -> dict:
        """
        Post-traitement pour déterminer message explicatif.
        """
        message = "Transaction suspecte" if result["alert"] else "Transaction normale"
        result["message"] = message
        return result

    def evaluate(self, transaction: dict) -> dict:
        """
        Évalue une transaction :
        1. Prétraitement
        2. Règles métier + modèle ML
        3. Post-traitement
        4. Logging ELK
        """
        try:
            processed_tx = self.preprocess(transaction)
            result = fraude_model.evaluate_transaction(processed_tx)
            result = self.postprocess(result)

            # Logging structuré
            logger.info({
                "event": "fraude_service_evaluation",
                "transaction_id": transaction.get("transaction_id"),
                "client_id": transaction.get("client_id"),
                "risque": result["risque"],
                "alert": result["alert"]
            })

            return result

        except Exception as e:
            logger.error({
                "event": "fraude_service_error",
                "transaction_id": transaction.get("transaction_id"),
                "client_id": transaction.get("client_id"),
                "error": str(e)
            })
            raise

# --- Singleton global
fraude_service = FraudeService()

# --- Exemple d'utilisation
if __name__ == "__main__":
    transaction_test = {
        "transaction_id": "TX2001",
        "client_id": "C300",
        "montant": 15000,
        "type": "virement",
        "historique_impaye": 2
    }
    result = fraude_service.evaluate(transaction_test)
    print(result)
