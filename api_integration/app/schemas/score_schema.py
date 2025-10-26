from pydantic import BaseModel, Field, validator
from typing import Optional

class ScoreRequest(BaseModel):
    client_id: str = Field(..., example="C1001", description="Identifiant unique du client")
    age: int = Field(..., ge=18, le=120, example=35, description="Âge du client")
    revenu: float = Field(..., gt=0, example=50000, description="Revenu annuel du client")
    historique_impaye: int = Field(..., ge=0, example=1, description="Nombre de dettes impayées")
    montant_credit: Optional[float] = Field(default=None, gt=0, example=15000, description="Montant du crédit demandé")

    @validator("age")
    def check_age(cls, v):
        if v < 18:
            raise ValueError("L'âge doit être supérieur ou égal à 18 ans")
        return v

class ScoreResponse(BaseModel):
    client_id: str = Field(..., description="ID du client")
    score: float = Field(..., ge=0, le=1, description="Score de crédit entre 0 et 1")
    decision: str = Field(..., description="Décision basée sur le score (accepté / refusé)")
    message: str = Field(..., description="Message explicatif ou recommandation")
