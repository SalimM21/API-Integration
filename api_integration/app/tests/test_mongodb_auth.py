import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.security.mongodb_auth import MongoDBAuthManager
from app.models.user import UserInDB
import os

@pytest.fixture
async def mongodb_auth():
    """Fixture pour créer une instance de test de MongoDBAuthManager"""
    auth_manager = MongoDBAuthManager()
    await auth_manager.initialize()
    yield auth_manager
    await auth_manager.close()

@pytest.fixture
async def test_user():
    """Fixture pour créer un utilisateur de test"""
    return {
        "username": "test_user",
        "access_token": "test_token",
        "hashed_password": "hashed_password"
    }

@pytest.mark.asyncio
async def test_mongodb_connection(mongodb_auth):
    """Test de la connexion à MongoDB"""
    db = await mongodb_auth.get_database()
    # Vérifier que la connexion est établie
    assert db is not None
    # Vérifier que nous pouvons exécuter une commande
    result = await db.command("ping")
    assert result["ok"] == 1

@pytest.mark.asyncio
async def test_user_validation(mongodb_auth, test_user):
    """Test de la validation de l'accès utilisateur"""
    db = await mongodb_auth.get_database()
    
    # Créer un utilisateur de test
    await db.users.insert_one(test_user)
    
    # Tester la validation avec des credentials valides
    is_valid = await mongodb_auth.validate_user_access(
        test_user["username"],
        test_user["access_token"]
    )
    assert is_valid is True
    
    # Tester la validation avec des credentials invalides
    is_valid = await mongodb_auth.validate_user_access(
        "invalid_user",
        "invalid_token"
    )
    assert is_valid is False
    
    # Nettoyer
    await db.users.delete_one({"username": test_user["username"]})

@pytest.mark.asyncio
async def test_conversation_saving(mongodb_auth, test_user):
    """Test de la sauvegarde des conversations"""
    conversation_data = {
        "user_id": test_user["username"],
        "message": "Test message",
        "response": [{"text": "Test response"}],
        "timestamp": "2025-11-08T12:00:00"
    }
    
    # Sauvegarder la conversation
    await mongodb_auth.save_conversation(conversation_data)
    
    # Vérifier que la conversation est sauvegardée
    db = await mongodb_auth.get_database()
    saved_conv = await db.conversations.find_one({
        "user_id": test_user["username"]
    })
    
    assert saved_conv is not None
    assert saved_conv["message"] == conversation_data["message"]
    assert saved_conv["response"] == conversation_data["response"]
    
    # Nettoyer
    await db.conversations.delete_one({"user_id": test_user["username"]})