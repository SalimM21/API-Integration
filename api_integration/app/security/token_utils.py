import jwt
from datetime import datetime, timedelta
from typing import List, Optional
from app.config import TEST_JWT_SECRET, TEST_JWT_ALGORITHM, TEST_JWT_ISSUER, TEST_JWT_AUDIENCE

# ---------------------------
# Génération de JWT pour tests
# ---------------------------
def generate_jwt(
    subject: str,
    roles: Optional[List[str]] = None,
    exp_minutes: int = 60
) -> str:
    """
    Génère un JWT signé pour tests.
    
    Args:
        subject (str): identifiant du user (sub)
        roles (List[str], optional): rôles assignés
        exp_minutes (int): durée de validité en minutes
    
    Returns:
        str: JWT encodé
    """
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
        "iss": TEST_JWT_ISSUER,
        "aud": TEST_JWT_AUDIENCE,
        "realm_access": {
            "roles": roles or []
        }
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
    return token

# ---------------------------
# Validation de JWT pour tests
# ---------------------------
def validate_jwt(token: str) -> dict:
    """
    Décode et valide un JWT pour tests.
    
    Args:
        token (str): JWT encodé
    
    Returns:
        dict: payload décodé
    """
    try:
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience=TEST_JWT_AUDIENCE,
            issuer=TEST_JWT_ISSUER
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Le token a expiré")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Token invalide : {str(e)}")

# ---------------------------
# Exemple d'utilisation
# ---------------------------
if __name__ == "__main__":
    test_token = generate_jwt("user123", roles=["admin", "analyst"])
    print("JWT généré :", test_token)
    
    payload = validate_jwt(test_token)
    print("Payload décodé :", payload)
