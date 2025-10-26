from fastapi import APIRouter, HTTPException, Depends
from app.schemas.fraude_schema import FraudeRequest, FraudeResponse
from app.models.fraude_model import fraude_model
from app.logging.elk_logger import logger
from app.auth.auth_handler import require_roles

router = APIRouter()

@router.post("/", response_model=FraudeResponse, summary="Détection de fraude")
def detect_fraude(request: FraudeRequest):
    """
    Endpoint POST /fraude
    - Valide le payload JSON
    - Applique règles métier et modèle ML
    - Retourne le score de risque et alerte
    """
    try:
        # Convertir Pydantic model en dict
        transaction = request.dict()

        # Évaluer la transaction via fraude_model
        result = fraude_model.evaluate_transaction(transaction)

        # Logging déjà fait dans fraude_model, mais log API supplémentaire
        logger.info({
            "event": "fraude_request_processed",
            "transaction_id": transaction.get("transaction_id"),
            "client_id": transaction.get("client_id"),
            "risque": result["risque"],
            "alert": result["alert"]
        })

        return FraudeResponse(**result)

    except Exception as e:
        logger.error({
            "event": "fraude_error",
            "transaction_id": getattr(request, "transaction_id", None),
            "client_id": getattr(request, "client_id", None),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Erreur lors de l'évaluation de la fraude")
