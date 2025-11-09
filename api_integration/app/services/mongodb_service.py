"""Service MongoDB pour la gestion des utilisateurs et des conversations"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.config.mongodb_config import get_mongodb_config

class MongoDBService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Établit la connexion à MongoDB"""
        if self.client is None:
            config = get_mongodb_config()
            mongodb = config['mongodb']
            
            # Construire l'URI de connexion
            uri = f"mongodb://{mongodb['auth']['credentials']['username']}:{mongodb['auth']['credentials']['password']}@{mongodb['connection']['host']}:{mongodb['connection']['port']}/?authSource=admin"
            
            # Créer le client
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client[mongodb['connection']['database']]
            
            # Vérifier la connexion
            await self.client.admin.command('ping')

    async def close(self):
        """Ferme la connexion à MongoDB"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son nom d'utilisateur"""
        if self.db is None:
            await self.connect()
        return await self.db.users.find_one({'username': username})

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crée un nouvel utilisateur"""
        if self.db is None:
            await self.connect()
        
        # Ajouter les timestamps
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = user_data['created_at']
        
        result = await self.db.users.insert_one(user_data)
        return str(result.inserted_id)

    async def save_conversation(self, conversation: Dict[str, Any]) -> str:
        """Sauvegarde une nouvelle conversation"""
        if self.db is None:
            await self.connect()
        
        # Ajouter les timestamps si non présents
        if 'metadata' not in conversation:
            conversation['metadata'] = {}
        
        now = datetime.utcnow()
        if 'created_at' not in conversation['metadata']:
            conversation['metadata']['created_at'] = now
        conversation['metadata']['updated_at'] = now
        
        result = await self.db.conversations.insert_one(conversation)
        return str(result.inserted_id)

    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les conversations d'un utilisateur"""
        if self.db is None:
            await self.connect()
        
        cursor = self.db.conversations.find(
            {'user_id': user_id}
        ).sort('metadata.updated_at', -1).limit(limit)
        
        return [conversation async for conversation in cursor]

    async def update_conversation(self, conversation_id: str, update_data: Dict[str, Any]) -> bool:
        """Met à jour une conversation existante"""
        if self.db is None:
            await self.connect()
        
        # Ajouter le timestamp de mise à jour
        if 'metadata' not in update_data:
            update_data['metadata'] = {}
        update_data['metadata']['updated_at'] = datetime.utcnow()
        
        result = await self.db.conversations.update_one(
            {'_id': conversation_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

# Instance globale du service
mongodb_service = MongoDBService()