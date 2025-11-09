from typing import Optional
import yaml
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from ..config import config

logger = logging.getLogger(__name__)

class MongoDBAuthManager:
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._config = self._load_config()

    def _load_config(self) -> dict:
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'config', 'auth', 'mongodb_auth.yaml'
        )
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config['mongodb']

    async def initialize(self):
        """Initialise la connexion MongoDB avec authentification"""
        try:
            # Construire l'URI de connexion avec auth
            username = os.getenv('MONGO_USERNAME', self._config['auth']['credentials']['username'])
            password = os.getenv('MONGO_PASSWORD', self._config['auth']['credentials']['password'])
            host = self._config['connection']['host']
            port = self._config['connection']['port']
            auth_source = self._config['auth']['source']

            uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
            
            # Créer le client avec les options de connexion
            self._client = AsyncIOMotorClient(
                uri,
                retryWrites=self._config['connection']['options']['retryWrites'],
                w=self._config['connection']['options']['w']
            )

            # Vérifier la connexion
            await self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB with authentication")

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def get_database(self):
        """Retourne la base de données configurée"""
        if not self._client:
            await self.initialize()
        return self._client[self._config['connection']['database']]

    async def close(self):
        """Ferme la connexion MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")

    async def validate_user_access(self, username: str, access_token: str) -> bool:
        """Valide l'accès utilisateur"""
        try:
            db = await self.get_database()
            user = await db[self._config['collections']['users']].find_one({
                "username": username,
                "access_token": access_token
            })
            return bool(user)
        except Exception as e:
            logger.error(f"Error validating user access: {e}")
            return False

    async def save_conversation(self, conversation_data: dict):
        """Sauvegarde une conversation dans MongoDB"""
        try:
            db = await self.get_database()
            await db[self._config['collections']['conversations']].insert_one(conversation_data)
            logger.info(f"Conversation saved for user: {conversation_data.get('user_id')}")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise

# Instance singleton
mongodb_auth = MongoDBAuthManager()