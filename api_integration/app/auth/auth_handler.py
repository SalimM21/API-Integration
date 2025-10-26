from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import requests
from app.config import KEYCLOAK_ISSUER, KEYCLOAK_ALGORITHMS, KEYCLOAK_CLIENT_ID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Récupération des JWKS de Keycloak / Okta ---
jwks_url = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"
jwks = requests.get(jwks_url).json()

def get_public_key(kid: str):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    raise HTTPException(status_code=401, detail="Clé publique non trouvée pour JWT")

def verify_jwt(token: str = Depends(oauth2_scheme)):
    """
    Vérifie le JWT et retourne le payload.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = get_public_key(unverified_header["kid"])
        payload = jwt.decode(
            token,
            key,
            algorithms=[KEYCLOAK_ALGORITHMS],
            audience=KEYCLOAK_CLIENT_ID,
            issuer=KEYCLOAK_ISSUER
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide : {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_roles(*roles):
    """
    Dépendance FastAPI pour vérifier que le JWT contient au moins un rôle autorisé.
    Usage: Depends(require_roles("admin", "analyst"))
    """
    def wrapper(payload: dict = Depends(verify_jwt)):
        token_roles = payload.get("realm_access", {}).get("roles", [])
        if not any(role in token_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle insuffisant pour accéder à cette ressource"
            )
        return payload
    return wrapper
