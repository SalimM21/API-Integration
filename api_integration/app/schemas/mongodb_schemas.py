"""Schémas Pydantic pour la validation des données MongoDB"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    """Schéma pour un message dans une conversation"""
    role: str = Field(..., pattern="^(user|bot)$")
    content: str
    timestamp: datetime

class ConversationMetadata(BaseModel):
    """Métadonnées d'une conversation"""
    created_at: datetime
    updated_at: datetime

class Conversation(BaseModel):
    """Schéma pour une conversation complète"""
    user_id: str
    messages: List[Message]
    metadata: ConversationMetadata

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    password: str

class UserResponse(UserBase):
    """Schéma pour la réponse utilisateur"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True