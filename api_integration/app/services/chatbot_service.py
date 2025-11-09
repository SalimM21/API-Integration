from typing import List, Dict, Any
import aiohttp
import logging
from datetime import datetime
from ..models.chat import ChatMessage
from ..config import config

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.rasa_url = config.get("rasa", {}).get("url", "http://localhost:5005")
        self.context_window = 5  # Nombre de messages à conserver pour le contexte

    async def process_message(self, message: str) -> List[Dict[str, Any]]:
        """Traite un message et retourne une réponse enrichie"""
        try:
            # Enrichir le message avec le contexte et les métadonnées
            enriched_message = await self._enrich_message(message)
            
            # Envoyer au modèle Rasa
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.rasa_url}/webhooks/rest/webhook",
                    json=enriched_message
                ) as response:
                    if response.status == 200:
                        bot_response = await response.json()
                        # Enrichir la réponse
                        return await self._enrich_response(bot_response, message)
                    else:
                        error_msg = await response.text()
                        logger.error(f"Rasa error: {error_msg}")
                        raise Exception("Failed to get response from chatbot")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    async def _enrich_message(self, message: str) -> Dict[str, Any]:
        """Enrichit le message avec des métadonnées et du contexte"""
        return {
            "message": message,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "language": await self._detect_language(message),
                "sentiment": await self._analyze_sentiment(message),
                "entities": await self._extract_entities(message)
            }
        }

    async def _enrich_response(
        self, 
        response: List[Dict[str, Any]], 
        original_message: str
    ) -> List[Dict[str, Any]]:
        """Enrichit la réponse avec des informations supplémentaires"""
        enriched_responses = []
        
        for msg in response:
            enriched_msg = {
                "text": msg["text"],
                "timestamp": datetime.utcnow().isoformat(),
                "context": {
                    "original_message": original_message,
                    "confidence": msg.get("confidence", 1.0),
                    "intent": msg.get("intent", {}).get("name", "unknown")
                },
                "suggestions": await self._generate_suggestions(msg["text"]),
                "additional_info": await self._fetch_additional_info(msg["text"])
            }
            enriched_responses.append(enriched_msg)
        
        return enriched_responses

    async def _detect_language(self, text: str) -> str:
        """Détecte la langue du message"""
        # TODO: Implémenter la détection de langue
        return "fr"  # Par défaut français

    async def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyse le sentiment du message"""
        # TODO: Implémenter l'analyse de sentiment
        return {
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0
        }

    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les entités nommées du message"""
        # TODO: Implémenter l'extraction d'entités
        return []

    async def _generate_suggestions(self, response_text: str) -> List[str]:
        """Génère des suggestions de suivi basées sur la réponse"""
        # TODO: Implémenter la génération de suggestions
        return [
            "Pouvez-vous m'en dire plus ?",
            "Comment puis-je vous aider davantage ?",
            "Souhaitez-vous des informations complémentaires ?"
        ]

    async def _fetch_additional_info(self, response_text: str) -> Dict[str, Any]:
        """Récupère des informations supplémentaires pertinentes"""
        # TODO: Implémenter la récupération d'informations
        return {
            "related_topics": [],
            "useful_links": [],
            "documentation": None
        }