"""
MercadoLibre API Client
=======================

Client for ingesting MercadoLibre consultations and questions.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json
import os


class MercadoLibreAPIClient:
    """Client for MercadoLibre API interactions"""

    def __init__(
        self,
        access_token: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize MercadoLibre API client

        Args:
            access_token: MercadoLibre API access token
            user_id: MercadoLibre user ID
        """
        self.access_token = access_token or os.getenv("MERCADOLIBRE_ACCESS_TOKEN")
        self.user_id = user_id or os.getenv("MERCADOLIBRE_USER_ID")
        self.base_url = "https://api.mercadolibre.com"

    def get_questions(
        self,
        item_id: Optional[str] = None,
        limit: int = 50,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get questions from MercadoLibre listings

        Args:
            item_id: Specific item ID (optional)
            limit: Maximum number of questions
            since: Get questions since this date

        Returns:
            List of questions
        """
        questions = []

        try:
            if item_id:
                # Get questions for specific item
                url = f"{self.base_url}/questions/search"
                params = {
                    "item_id": item_id,
                    "limit": limit,
                    "access_token": self.access_token
                }

                if since:
                    params["date_from"] = since.isoformat()

                # In a real implementation, make HTTP request here
                # For now, return empty list as placeholder
                logger.info(f"Would fetch questions for item {item_id}")

            else:
                # Get questions from all user's items
                if not self.user_id:
                    logger.warning("User ID required for fetching all questions")
                    return questions

                # In a real implementation, fetch user's items first
                # Then fetch questions for each item
                logger.info(f"Would fetch questions for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error fetching MercadoLibre questions: {e}")

        return questions

    def get_messages(
        self,
        limit: int = 50,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get messages from MercadoLibre

        Args:
            limit: Maximum number of messages
            since: Get messages since this date

        Returns:
            List of messages
        """
        messages = []

        try:
            if not self.user_id:
                logger.warning("User ID required for fetching messages")
                return messages

            # In a real implementation, make HTTP request to messages endpoint
            # url = f"{self.base_url}/messages/search"
            # params = {
            #     "user_id": self.user_id,
            #     "limit": limit,
            #     "access_token": self.access_token
            # }
            # if since:
            #     params["date_from"] = since.isoformat()

            logger.info(f"Would fetch messages for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error fetching MercadoLibre messages: {e}")

        return messages

    def normalize_interaction(
        self,
        data: Dict,
        interaction_type: str
    ) -> Dict:
        """
        Normalize MercadoLibre interaction to unified schema

        Args:
            data: Raw MercadoLibre API data
            interaction_type: Type of interaction (question, message)

        Returns:
            Normalized interaction data
        """
        normalized = {
            "id": data.get("id", ""),
            "platform": "mercadolibre",
            "type": interaction_type,
            "timestamp": self._parse_timestamp(data.get("date_created")),
            "user": {
                "id": data.get("from", {}).get("user_id", "") if isinstance(data.get("from"), dict) else "",
                "name": data.get("from", {}).get("nickname", "") if isinstance(data.get("from"), dict) else "",
                "is_business": False,
            },
            "content": data.get("text", data.get("question", "")),
            "context": {
                "item_id": data.get("item_id", ""),
                "listing_url": f"https://articulo.mercadolibre.com.uy/{data.get('item_id', '')}" if data.get("item_id") else "",
                "category": data.get("category", ""),
            },
            "engagement": {
                "likes": 0,
                "replies": 1 if data.get("answer") else 0,
                "shares": 0,
            },
            "metadata": {
                "is_question": interaction_type == "question",
                "requires_response": interaction_type == "question" and not data.get("answer"),
                "sentiment": "neutral",
                "topics": self._extract_topics(data.get("text", data.get("question", ""))),
            },
        }

        return normalized

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> str:
        """Parse timestamp to ISO format"""
        if not timestamp_str:
            return datetime.now().isoformat()

        try:
            # MercadoLibre uses ISO 8601 format
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.isoformat()
        except:
            return datetime.now().isoformat()

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()

        if any(word in text_lower for word in ["precio", "costo", "cuanto", "valor"]):
            topics.append("pricing")
        if any(word in text_lower for word in ["envio", "entrega", "shipping"]):
            topics.append("shipping")
        if any(word in text_lower for word in ["stock", "disponible", "hay"]):
            topics.append("availability")
        if any(word in text_lower for word in ["caracteristicas", "especificaciones", "medidas"]):
            topics.append("specifications")

        return topics

    def _is_question(self, text: str) -> bool:
        """Check if text is a question"""
        question_indicators = ["?", "cuanto", "cuál", "qué", "cómo", "dónde", "cuándo"]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators) or "?" in text

    def _requires_response(self, text: str) -> bool:
        """Check if interaction requires response"""
        response_indicators = ["necesito", "quiero", "busco", "consulta", "información"]
        text_lower = text.lower()
        return self._is_question(text) or any(indicator in text_lower for indicator in response_indicators)
