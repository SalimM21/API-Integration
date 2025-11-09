"""Routes pour la gestion des utilisateurs et des conversations"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.mongodb_schemas import UserCreate, UserResponse, Conversation
from app.services.mongodb_service import mongodb_service
from datetime import datetime

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Crée un nouvel utilisateur"""
    # Vérifier si l'utilisateur existe déjà
    existing_user = await mongodb_service.get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Créer le nouvel utilisateur
    user_data = user.model_dump()
    # TODO: Hasher le mot de passe avant de le stocker
    user_id = await mongodb_service.create_user(user_data)
    
    # Récupérer l'utilisateur créé
    created_user = await mongodb_service.get_user(user.username)
    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return UserResponse(**created_user)

@router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str):
    """Récupère les informations d'un utilisateur"""
    user = await mongodb_service.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(conversation: Conversation):
    """Crée une nouvelle conversation"""
    # Vérifier si l'utilisateur existe
    user = await mongodb_service.get_user(conversation.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Sauvegarder la conversation
    conversation_id = await mongodb_service.save_conversation(conversation.model_dump())
    if not conversation_id:
        raise HTTPException(status_code=500, detail="Failed to save conversation")
    
    return conversation

@router.get("/conversations/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(user_id: str, limit: int = 10):
    """Récupère les conversations d'un utilisateur"""
    # Vérifier si l'utilisateur existe
    user = await mongodb_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conversations = await mongodb_service.get_user_conversations(user_id, limit)
    return conversations