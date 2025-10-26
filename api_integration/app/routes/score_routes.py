from fastapi import APIRouter, HTTPException, Depends
from app.schemas.score_schema import ScoreRequest, ScoreResponse
from app.models.scoring_model import scoring_model
from app.logging.elk_logger import logger
from app.auth.auth_handler import require_roles

router = APIRouter()

@router.post("/", response_model=ScoreResponse, summary="Calcul du score crédit")
def get_score(request: ScoreRequest):
    """
    Endpoint POST /score
    - Valide le payload JSON
    - Appelle le modèle de scoring
    - Retourne le score et la décision
    """
    try:
        # Calcul du score
        score = scoring_model.predict_score(request.dict())

        # Décision simple
        from app.config import SCORE_THRESHOLD
        decision = "accepté" if score >= SCORE_THRESHOLD else "refusé"
        message = f"Score = {score}, décision = {decision}"

        # Logging structuré
        logger.info({
            "event": "scoring_request",
            "client_id": request.client_id,
            "score": score,
            "decision": decision
        })

        return ScoreResponse(
            client_id=request.client_id,
            score=score,
            decision=decision,
            message=message
        )

    except Exception as e:
        logger.error({
            "event": "scoring_error",
            "client_id": request.client_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Erreur lors du calcul du score")
