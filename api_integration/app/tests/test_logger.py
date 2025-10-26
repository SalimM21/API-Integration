"""
Tests pour le logging ELK (app/logging/elk_logger.py).

Objectifs :
 - Vérifier que la fonction mapLogRecord du handler retourne du JSON structuré attendu.
 - Vérifier que le logger global appelle bien le handler.emit lors d'un logger.info(...)
 - Si l'implémentation expose un client Elasticsearch (es / es_client), vérifier qu'une indexation est tentée
   lorsqu'un dict est loggé (cas où le code module utiliserait es.index).
 
Ces tests utilisent monkeypatch pour éviter tout appel réseau réel.
"""
import logging
import json
import types
import pytest

from app.logging import elk_logger


def make_log_record(msg, level=logging.INFO, name="elk_logger.test"):
    """
    Crée un LogRecord utilisable par mapLogRecord/emit.
    """
    return logging.LogRecord(name=name, level=level, pathname=__file__, lineno=1, msg=msg, args=(), exc_info=None)


def test_mapLogRecord_returns_json_when_msg_is_dict():
    """
    Vérifie que mapLogRecord retourne une JSON string contenant les champs attendus
    quand record.msg est un dict.
    """
    handler = None
    # Cherche un handler de type ELKHTTPHandler dans elk_logger module
    for h in getattr(elk_logger, "logger", logging.getLogger()).handlers:
        # On identifie par le nom de classe défini dans le module
        if h.__class__.__name__ == "ELKHTTPHandler" or hasattr(h, "mapLogRecord"):
            handler = h
            break

    # Si le handler spécifique n'existe pas (implémentation différente), on crée une instance locale
    if handler is None and hasattr(elk_logger, "ELKHTTPHandler"):
        handler = elk_logger.ELKHTTPHandler(host="localhost:5044", url="/test/_doc", method="POST")
    assert handler is not None, "Impossible d'obtenir ELKHTTPHandler pour le test"

    # Crée un LogRecord dont msg est un dict
    record = make_log_record({"event": "unit_test", "transaction_id": "T123", "client_id": "C1"})
    mapped = handler.mapLogRecord(record)
    # mapLogRecord retourne une chaîne JSON (selon implémentation)
    assert isinstance(mapped, str)
    # Parse JSON
    parsed = json.loads(mapped)
    # Champs attendus
    assert "message" in parsed or "event" in parsed
    assert parsed.get("event") == "unit_test" or parsed.get("message")
    # Vérifier présence hostname/service/level if provided by implementation
    assert "level" in parsed or "logger_name" in parsed or "service" in parsed


def test_logger_emit_called_on_info(monkeypatch):
    """
    Vérifie que le handler.emit est appelé quand on logge via elk_logger.logger.info(...)
    """
    logger = getattr(elk_logger, "logger", None)
    assert logger is not None, "Module elk_logger n'expose pas 'logger'"

    # Choisir un handler sur lequel patcher emit
    target_handler = None
    for h in logger.handlers:
        # On patchera le premier handler trouvable
        target_handler = h
        break

    assert target_handler is not None, "Aucun handler disponible sur elk_logger.logger"

    called = {"count": 0, "record": None}

    def fake_emit(rec):
        called["count"] += 1
        called["record"] = rec

    # Patch emit
    monkeypatch.setattr(target_handler, "emit", fake_emit, raising=True)

    # Appel du logger avec un dict (structure attendue)
    logger.info({"event": "test_info_emit", "client_id": "Cxyz"})

    assert called["count"] >= 1, "Le handler.emit n'a pas été appelé"
    # Vérifier que le record contient le message (getMessage) et que c'est un dict ou string
    rec = called["record"]
    assert hasattr(rec, "getMessage")
    msg = rec.getMessage()
    # msg peut être dict (selon implémentation) ou stringified JSON
    assert (isinstance(msg, dict) and msg.get("event") == "test_info_emit") or ("test_info_emit" in str(msg))


def test_es_index_called_when_es_client_present(monkeypatch):
    """
    Si le module expose un client Elasticsearch (ex: es or es_client), patcher sa méthode index()
    et vérifier qu'elle est appelée lorsque l'on logge un dict (implémentations qui utilisent es.index).
    Ce test est tolérant : si le module n'expose pas d'objet es/es_client, on le considère comme non applicable.
    """
    # Cherche es or es_client
    es_obj = None
    if hasattr(elk_logger, "es"):
        es_obj = getattr(elk_logger, "es")
        es_name = "es"
    elif hasattr(elk_logger, "es_client"):
        es_obj = getattr(elk_logger, "es_client")
        es_name = "es_client"
    else:
        es_obj = None
        es_name = None

    if es_obj is None:
        pytest.skip("Aucun client Elasticsearch exposé dans elk_logger (es / es_client) — test non applicable")

    called = {"count": 0, "args": None, "kwargs": None}

    def fake_index(index, document=None, **kwargs):
        called["count"] += 1
        called["args"] = (index, document)
        called["kwargs"] = kwargs
        # Simuler une réponse ES
        return {"_index": index, "_id": "1", "result": "created"}

    # Patch la méthode index sur l'objet es
    monkeypatch.setattr(es_obj, "index", fake_index, raising=True)

    # Logger un event structuré qu'une implémentation pourrait envoyer via es.index
    elk_logger.logger.info({"event": "test_es_index", "transaction_id": "T999", "client_id": "C999"})

    assert called["count"] >= 1, f"es.index n'a pas été appelé sur {es_name}"
    index_arg, doc_arg = called["args"]
    assert isinstance(index_arg, str)
    # Document doit contenir les clés qu'on a loggées
    assert doc_arg is not None
    # doc_arg peut être dict ou json string ; gérer les deux cas
    if isinstance(doc_arg, str):
        parsed = json.loads(doc_arg)
    else:
        parsed = doc_arg
    assert parsed.get("event") == "test_es_index" or parsed.get("transaction_id") == "T999"
