import os
import pickle
import numpy as np
from app.config import SCORING_MODEL_PATH

class ScoringModel:
    def __init__(self, model_path=SCORING_MODEL_PATH):
        self.model_path = model_path
        self.model = self.load_model()

    def load_model(self):
        """
        Charge le modèle ML depuis un fichier Pickle (ou retourne un modèle fictif).
        """
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    model = pickle.load(f)
                print(f"[INFO] Modèle chargé depuis {self.model_path}")
                return model
            except Exception as e:
                print(f"[ERROR] Impossible de charger le modèle : {e}")
        # Modèle fictif si fichier inexistant
        print("[WARN] Aucun modèle trouvé, utilisation du modèle fictif")
        return None

    def predict_score(self, input_data: dict) -> float:
        """
        Prédit le score d'un client à partir d'un dictionnaire d'attributs.
        Exemple input_data:
        {
            "age": 35,
            "revenu": 50000,
            "historique_impaye": 1
        }
        Retourne un score entre 0 et 1.
        """
        if self.model:
            # Ici on suppose que le modèle a une méthode predict_proba
            features = np.array([list(input_data.values())])
            score = self.model.predict_proba(features)[0][1]  # Probabilité classe 1
            return float(score)
        else:
            # Modèle fictif : calcul simple
            age = input_data.get("age", 30)
            revenu = input_data.get("revenu", 30000)
            historique_impaye = input_data.get("historique_impaye", 0)
            # Score simulé entre 0 et 1
            score = max(0, min(1, 0.3 + 0.005 * (revenu/1000) - 0.05*historique_impaye + 0.01*(age/10)))
            return round(score, 3)

# --- Singleton pour l'utilisation globale
scoring_model = ScoringModel()

# Exemple d'utilisation
if __name__ == "__main__":
    test_input = {"age": 40, "revenu": 60000, "historique_impaye": 0}
    score = scoring_model.predict_score(test_input)
    print(f"Score prédit: {score}")
