import requests
from typing import List, Dict
from app.config import KEYCLOAK_ISSUER, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET

class KeycloakClient:
    """
    Client pour interagir avec Keycloak / Okta.
    Fournit récupération des rôles et introspection de token.
    """

    def __init__(self, issuer=KEYCLOAK_ISSUER, client_id=KEYCLOAK_CLIENT_ID, client_secret=KEYCLOAK_CLIENT_SECRET):
        self.issuer = issuer
        self.client_id = client_id
        self.client_secret = client_secret
        self.introspect_url = f"{self.issuer}/protocol/openid-connect/token/introspect"

    def introspect_token(self, token: str) -> Dict:
        """
        Vérifie la validité du token auprès de Keycloak.
        Retourne le payload si valide.
        """
        data = {
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.introspect_url, data=data)
        if response.status_code != 200:
            raise ValueError(f"Erreur introspection token : {response.text}")
        result = response.json()
        if not result.get("active"):
            raise ValueError("Token inactif ou invalide")
        return result

    def get_roles(self, token: str) -> List[str]:
        """
        Récupère les rôles de l'utilisateur à partir du token.
        """
        payload = self.introspect_token(token)
        roles = payload.get("realm_access", {}).get("roles", [])
        return roles

# --- Exemple d'utilisation
if __name__ == "__main__":
    client = KeycloakClient()
    sample_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # Remplacer par un token valide

    try:
        roles = client.get_roles(sample_token)
        print("Rôles récupérés :", roles)
    except ValueError as e:
        print("Erreur :", e)
