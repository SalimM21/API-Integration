from fastapi import APIRouter, HTTPException, Depends
from ..models.chat import ChatMessage
from ..services.chatbot_service import ChatbotService
from ..security.mongodb_auth import mongodb_auth
from ..auth.auth_utils import get_current_user
from typing import List
import logging

router = APIRouter()
chatbot_service = ChatbotService()
logger = logging.getLogger(__name__)

@router.post("/chatbot", response_model=List[dict])
async def chat_endpoint(
    message: ChatMessage,
    current_user = Depends(get_current_user)
):
    try:
        # Valider l'accès utilisateur
        if not await mongodb_auth.validate_user_access(
            current_user.username, 
            current_user.access_token
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid user credentials"
            )

        # Traiter le message
        response = await chatbot_service.process_message(message.message)

        # Sauvegarder la conversation
        await mongodb_auth.save_conversation({
            "user_id": current_user.username,
            "message": message.message,
            "response": response,
            "timestamp": message.timestamp
        })

        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )