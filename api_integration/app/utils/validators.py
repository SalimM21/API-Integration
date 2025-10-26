from typing import Any, Dict
from fastapi import HTTPException, status

# ---------------------------
# Validation générale des champs
# ---------------------------
def validate_age(age: int):
    """
    Vérifie que l'âge est valide (>=18 ans et <=120 ans).
    """
    if not (18 <= age <= 120):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"L'âge doit être compris entre 18 et 120 ans, reçu : {age}"
        )

def validate_revenu(revenu: float):
    """
    Vérifie que le revenu est positif.
    """
    if revenu <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Le revenu doit être positif, reçu : {revenu}"
        )

def validate_montant_credit(montant: float):
    """
    Vérifie que le montant du crédit est positif.
    """
    if montant <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Le montant du crédit doit être positif, reçu : {montant}"
        )

def validate_historique_impaye(historique: int):
    """
    Vérifie que l'historique impayé est >=0.
    """
    if historique < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"L'historique impayé doit être >= 0, reçu : {historique}"
        )

# ---------------------------
# Validation transaction fraude
# ---------------------------
def validate_montant_transaction(montant: float):
    """
    Vérifie que le montant de la transaction est positif.
    """
    if montant <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Le montant de la transaction doit être positif, reçu : {montant}"
        )

def validate_type_transaction(tx_type: str, allowed_types=None):
    """
    Vérifie que le type de transaction est parmi les types autorisés.
    """
    if allowed_types is None:
        allowed_types = ["virement", "paiement", "retrait"]
    if tx_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Type de transaction invalide : {tx_type}, autorisés : {allowed_types}"
        )

# ---------------------------
# Validation globale d'un payload score
# ---------------------------
def validate_score_payload(payload: Dict[str, Any]):
    validate_age(payload.get("age"))
    validate_revenu(payload.get("revenu"))
    if "montant_credit" in payload and payload["montant_credit"] is not None:
        validate_montant_credit(payload["montant_credit"])
    validate_historique_impaye(payload.get("historique_impaye"))

# ---------------------------
# Validation globale d'une transaction fraude
# ---------------------------
def validate_fraude_payload(payload: Dict[str, Any]):
    validate_montant_transaction(payload.get("montant"))
    validate_type_transaction(payload.get("type"))
    if "historique_impaye" in payload:
        validate_historique_impaye(payload.get("historique_impaye"))

# ---------------------------
# Exemple d'utilisation
# ---------------------------
if __name__ == "__main__":
    score_payload = {"age": 35, "revenu": 50000, "historique_impaye": 1, "montant_credit": 15000}
    validate_score_payload(score_payload)
    
    fraude_payload = {"montant": 15000, "type": "virement", "historique_impaye": 2}
    validate_fraude_payload(fraude_payload)
