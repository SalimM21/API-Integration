from fastapi import Depends, HTTPException, status
from app.auth.auth_handler import verify_jwt

def require_roles(*allowed_roles):
    """
    Dépendance FastAPI pour vérifier que le JWT contient au moins un rôle autorisé.
    Usage: Depends(require_roles("admin", "analyst"))
    """
    def wrapper(payload: dict = Depends(verify_jwt)):
        """
        Vérifie que le JWT contient au moins un rôle autorisé.
        """
        token_roles = payload.get("realm_access", {}).get("roles", [])
        if not any(role in token_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle insuffisant pour accéder à cette ressource"
            )
        return payload
    return wrapper
