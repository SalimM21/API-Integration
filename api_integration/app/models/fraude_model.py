import random
from app.config import FRAUDE_ALERT_THRESHOLD
from app.logging.elk_logger import logger

class FraudeModel:
    """
    Modèle de détection de fraude combinant règles métier et ML fictif.
    """

    def __init__(self):
        # Ici on pourrait charger un modèle ML réel (Pickle, ONNX)
        self.model = None  # Modèle fictif

    def apply_rules(self, transaction: dict) -> float:
        """
        Applique des règles métier simples pour détecter les transactions suspectes.
        Retourne un score de risque entre 0 et 1.
        """
        score = 0.0

        # Règle 1 : montant élevé
        if transaction.get("montant", 0) > 10000:
            score += 0.4

        # Règle 2 : type de transaction suspect
        if transaction.get("type") in ["retrait", "virement"]:
            score += 0.2

        # Règle 3 : historique du client (fictif)
        historique_impaye = transaction.get("historique_impaye", 0)
        score += 0.1 * historique_impaye

        return min(score, 1.0)

    def predict_ml(self, transaction: dict) -> float:
        """
        Prédit un score de risque via ML fictif.
        """
        if self.model:
            # Ici on appellerait le modèle réel
            # score = self.model.predict_proba(features)[0][1]
            score = 0.0
        else:
            # Score aléatoire pour test
            score = random.uniform(0, 0.5)
        return score

    def evaluate_transaction(self, transaction: dict) -> dict:
        """
        Combine règles métier et ML pour retourner le risque final et alerte.
        """
        score_rules = self.apply_rules(transaction)
        score_ml = self.predict_ml(transaction)
        risque = round(min(1.0, score_rules + score_ml), 3)

        alert = risque >= FRAUDE_ALERT_THRESHOLD

        # Logging structuré vers ELK
        logger.info({
            "event": "fraude_evaluation",
            "transaction_id": transaction.get("transaction_id"),
            "client_id": transaction.get("client_id"),
            "risque": risque,
            "alert": alert
        })

        return {
            "transaction_id": transaction.get("transaction_id"),
            "client_id": transaction.get("client_id"),
            "risque": risque,
            "alert": alert,
            "message": "Transaction suspecte" if alert else "Transaction normale"
        }

# --- Singleton global
fraude_model = FraudeModel()

# --- Exemple d'utilisation
if __name__ == "__main__":
    transaction_test = {
        "transaction_id": "TX1001",
        "client_id": "C200",
        "montant": 15000,
        "type": "virement",
        "historique_impaye": 2
    }
    result = fraude_model.evaluate_transaction(transaction_test)
    print(result)
