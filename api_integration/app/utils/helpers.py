import hashlib
import json
from datetime import datetime

# ---------------------------
# Hashing
# ---------------------------
def hash_string(value: str, algorithm: str = "sha256") -> str:
    """
    Retourne le hash d'une chaîne de caractères.
    
    Args:
        value (str): Chaîne à hasher
        algorithm (str): Algorithme de hashage ('sha256', 'md5', 'sha1')
        
    Returns:
        str: Hash hexadécimal
    """
    value_bytes = value.encode("utf-8")
    if algorithm.lower() == "sha256":
        return hashlib.sha256(value_bytes).hexdigest()
    elif algorithm.lower() == "md5":
        return hashlib.md5(value_bytes).hexdigest()
    elif algorithm.lower() == "sha1":
        return hashlib.sha1(value_bytes).hexdigest()
    else:
        raise ValueError(f"Algorithme de hash inconnu : {algorithm}")

# ---------------------------
# JSON utils
# ---------------------------
def pretty_json(data: dict) -> str:
    """
    Retourne une chaîne JSON formatée (indentée).
    """
    return json.dumps(data, indent=4, ensure_ascii=False)

# ---------------------------
# Date/heure utils
# ---------------------------
def current_timestamp(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Retourne l'heure actuelle sous forme de chaîne formatée.
    """
    return datetime.now().strftime(format)

# ---------------------------
# Validation / Normalisation
# ---------------------------
def normalize_string(value: str) -> str:
    """
    Supprime les espaces superflus et met en minuscule.
    """
    if not isinstance(value, str):
        return value
    return " ".join(value.strip().lower().split())

def safe_float(value, default: float = 0.0) -> float:
    """
    Convertit une valeur en float, renvoie default si échec.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# ---------------------------
# Exemple d'utilisation
# ---------------------------
if __name__ == "__main__":
    print(hash_string("password123"))
    print(pretty_json({"client_id": "C101", "score": 0.85}))
    print(current_timestamp())
    print(normalize_string("  ExEmPle STRING  "))
    print(safe_float("12.34"))
    print(safe_float("invalid", default=-1))
