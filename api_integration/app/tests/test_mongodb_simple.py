import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import yaml

@pytest.fixture(scope="function")
async def mongodb_client(event_loop):
    """Configure la connexion de test à MongoDB"""
    test_config = {
        'mongodb': {
            'auth': {
                'enabled': True,
                'mechanism': 'SCRAM-SHA-256',
                'source': 'admin',
                'credentials': {
                    'username': 'test_user',
                    'password': 'test_password'
                }
            },
            'connection': {
                'host': 'localhost',
                'port': 27018,
                'database': 'test_db'
            }
        }
    }

    # Créer la connexion
    uri = f"mongodb://{test_config['mongodb']['auth']['credentials']['username']}:{test_config['mongodb']['auth']['credentials']['password']}@{test_config['mongodb']['connection']['host']}:{test_config['mongodb']['connection']['port']}/?authSource=admin"
    
    client = AsyncIOMotorClient(uri)
    
    # Vérifier la connexion
    try:
        await client.admin.command('ping')
    except Exception as e:
        client.close()
        pytest.fail(f"Impossible de se connecter à MongoDB: {str(e)}")
    
    yield client
    
    # Nettoyer après les tests
    try:
        db = client[test_config['mongodb']['connection']['database']]
        await db.users.delete_many({})
        await db.conversations.delete_many({})
    finally:
        client.close()

@pytest.fixture(scope="function")
async def mongodb_db(mongodb_client):
    """Retourne la base de données de test"""
    return mongodb_client['test_db']

class TestMongoDBAuth:

    @pytest.mark.asyncio
    async def test_mongodb_connection(self, mongodb_client):
        """Test la connexion à MongoDB"""
        # Vérifier que nous pouvons exécuter une commande
        result = await mongodb_client.admin.command('ping')
        assert result['ok'] == 1.0

    @pytest.mark.asyncio
    async def test_crud_operations(self, mongodb_db):
        """Test les opérations CRUD de base"""
        # Test Create
        test_user = {
            'username': 'test_user',
            'email': 'test@example.com',
            'access_token': 'test_token'
        }
        result = await mongodb_db.users.insert_one(test_user)
        assert result.inserted_id is not None

        # Test Read
        user = await mongodb_db.users.find_one({'username': 'test_user'})
        assert user is not None
        assert user['email'] == 'test@example.com'

        # Test Update
        update_result = await mongodb_db.users.update_one(
            {'username': 'test_user'},
            {'$set': {'email': 'updated@example.com'}}
        )
        assert update_result.modified_count == 1

        # Verify Update
        updated_user = await mongodb_db.users.find_one({'username': 'test_user'})
        assert updated_user['email'] == 'updated@example.com'

        # Test Delete
        delete_result = await mongodb_db.users.delete_one({'username': 'test_user'})
        assert delete_result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_conversation_storage(self, mongodb_db):
        """Test le stockage des conversations"""
        # Créer une conversation
        conversation = {
            'user_id': 'test_user',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Hello',
                    'timestamp': '2025-11-08T12:00:00'
                },
                {
                    'role': 'bot',
                    'content': 'Hi there!',
                    'timestamp': '2025-11-08T12:00:01'
                }
            ],
            'metadata': {
                'created_at': '2025-11-08T12:00:00',
                'updated_at': '2025-11-08T12:00:01'
            }
        }

        # Sauvegarder la conversation
        result = await mongodb_db.conversations.insert_one(conversation)
        assert result.inserted_id is not None

        # Récupérer la conversation
        saved_conv = await mongodb_db.conversations.find_one({'user_id': 'test_user'})
        assert saved_conv is not None
        assert len(saved_conv['messages']) == 2
        assert saved_conv['messages'][0]['content'] == 'Hello'