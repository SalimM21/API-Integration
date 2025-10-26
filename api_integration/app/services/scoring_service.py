from app.models.scoring_model import scoring_model
from app.config import SCORE_THRESHOLD
from app.logging.elk_logger import logger

class ScoringService:
    """
    Service de calcul du score client :
    - Prétraitement des données
    - Appel du modèle ML
    - Post-traitement et décision
    """

    def preprocess(self, data: dict) -> dict:
        """
        Prétraitement des données clients avant scoring.
        Exemple : normalisation, création de features dérivées.
        """
        processed = data.copy()

        # Feature dérivée : revenu / 1000
        processed["revenu_k"] = processed.get("revenu", 0) / 1000

        # Exemple : cap sur historique_impaye
        processed["historique_impaye"] = min(processed.get("historique_impaye", 0), 10)

        return processed

    def postprocess(self, score: float) -> dict:
        """
        Détermine la décision et message basé sur le score.
        """
        decision = "accepté" if score >= SCORE_THRESHOLD else "refusé"
        message = f"Score = {score}, décision = {decision}"
        return {
            "score": score,
            "decision": decision,
            "message": message
        }

    def calculate_score(self, client_data: dict) -> dict:
        """
        Calcule le score complet pour un client :
        1. Prétraitement
        2. Appel modèle ML
        3. Post-traitement
        4. Logging ELK
        """
        try:
            processed_data = self.preprocess(client_data)
            score = scoring_model.predict_score(processed_data)
            result = self.postprocess(score)

            # Logging structuré
            logger.info({
                "event": "scoring_service_calculation",
                "client_id": client_data.get("client_id"),
                "score": result["score"],
                "decision": result["decision"]
            })

            return result

        except Exception as e:
            logger.error({
                "event": "scoring_service_error",
                "client_id": client_data.get("client_id"),
                "error": str(e)
            })
            raise

# --- Singleton global
scoring_service = ScoringService()

# --- Exemple d'utilisation
if __name__ == "__main__":
    client_test = {"client_id": "C101", "age": 35, "revenu": 50000, "historique_impaye": 1}
    result = scoring_service.calculate_score(client_test)
    print(result)
