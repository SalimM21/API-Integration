from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class FraudeRequest(BaseModel):
    transaction_id: str = Field(..., example="TX12345", description="Identifiant unique de la transaction")
    client_id: str = Field(..., example="C1001", description="Identifiant du client")
    montant: float = Field(..., gt=0, example=2000.0, description="Montant de la transaction")
    type: str = Field(..., example="virement", description="Type de transaction")
    devise: str = Field(default="MAD", example="MAD", description="Devise de la transaction")
    date_transaction: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Date et heure de la transaction")

    @validator("type")
    def check_transaction_type(cls, v):
        allowed_types = ["virement", "paiement", "retrait", "depôt"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Type de transaction invalide : {v}. Types autorisés: {allowed_types}")
        return v.lower()

class FraudeResponse(BaseModel):
    transaction_id: str = Field(..., description="ID de la transaction")
    client_id: str = Field(..., description="ID du client")
    risque: float = Field(..., ge=0, le=1, description="Score de risque (0 = faible, 1 = élevé)")
    alert: bool = Field(..., description="Indique si la transaction déclenche une alerte fraude")
    message: str = Field(..., description="Message explicatif ou recommandation")
