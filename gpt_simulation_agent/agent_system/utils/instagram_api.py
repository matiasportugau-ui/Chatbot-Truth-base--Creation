"""
Instagram API Client

Handles Instagram Graph API interactions for ingesting real interactions.
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime
import requests
from loguru import logger


class InstagramAPIClient:
    """Client for Instagram Graph API"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        business_account_id: Optional[str] = None,
        api_version: str = "v18.0",
    ):
        """
        Initialize Instagram API client

        Args:
            app_id: Instagram App ID
            app_secret: Instagram App Secret
            access_token: Access Token
            business_account_id: Business Account ID
            api_version: API version (default: v18.0)
        """
        self.app_id = app_id or os.getenv("INSTAGRAM_APP_ID")
        self.app_secret = app_secret or os.getenv("INSTAGRAM_APP_SECRET")
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.business_account_id = business_account_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        self.api_version = api_version or os.getenv("INSTAGRAM_API_VERSION", "v18.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        if not self.access_token:
            logger.warning("Instagram Access Token not provided")

    def get_media(self, limit: int = 100, since: Optional[datetime] = None) -> List[Dict]:
        """
        Get media posts from Instagram business account

        Args:
            limit: Maximum number of posts
            since: Start date

        Returns:
            List of media data
        """
        if not self.business_account_id or not self.access_token:
            raise ValueError("Business Account ID and Access Token required")

        url = f"{self.base_url}/{self.business_account_id}/media"
        params = {
            "access_token": self.access_token,
            "fields": "id,caption,like_count,comments_count,timestamp,permalink",
            "limit": min(limit, 100),
        }

        if since:
            params["since"] = int(since.timestamp())

        media = []
        try:
            response = self._make_request(url, params)
            media = response.get("data", [])

            # Handle pagination
            while len(media) < limit and "paging" in response:
                next_url = response["paging"].get("next")
                if next_url:
                    response = requests.get(next_url).json()
                    media.extend(response.get("data", []))
                else:
                    break

        except Exception as e:
            logger.error(f"Error fetching Instagram media: {e}")

        return media[:limit]

    def get_comments(self, media_id: str, limit: int = 100) -> List[Dict]:
        """
        Get comments for a media post

        Args:
            media_id: Media ID
            limit: Maximum number of comments

        Returns:
            List of comment data
        """
        if not self.access_token:
            raise ValueError("Access Token required")

        url = f"{self.base_url}/{media_id}/comments"
        params = {
            "access_token": self.access_token,
            "fields": "id,text,timestamp,username,like_count",
            "limit": min(limit, 100),
        }

        comments = []
        try:
            response = self._make_request(url, params)
            comments = response.get("data", [])

            # Handle pagination
            while len(comments) < limit and "paging" in response:
                next_url = response["paging"].get("next")
                if next_url:
                    response = requests.get(next_url).json()
                    comments.extend(response.get("data", []))
                else:
                    break

        except Exception as e:
            logger.error(f"Error fetching Instagram comments: {e}")

        return comments[:limit]

    def get_direct_messages(self, limit: int = 100) -> List[Dict]:
        """
        Get direct messages (Note: Instagram DMs require special permissions)

        Args:
            limit: Maximum number of messages

        Returns:
            List of message data
        """
        # Instagram DMs require Instagram Messaging API
        # This is a placeholder implementation
        logger.warning("Instagram DMs require Instagram Messaging API setup")
        return []

    def normalize_interaction(self, data: Dict, interaction_type: str) -> Dict:
        """
        Normalize Instagram interaction to unified schema

        Args:
            data: Raw Instagram API data
            interaction_type: Type of interaction (post, comment, dm)

        Returns:
            Normalized interaction data
        """
        normalized = {
            "id": data.get("id", ""),
            "platform": "instagram",
            "type": interaction_type,
            "timestamp": self._parse_timestamp(data.get("timestamp")),
            "user": {
                "id": data.get("username", ""),
                "name": data.get("username", ""),
                "is_business": False,
            },
            "content": data.get("text", "") or data.get("caption", ""),
            "context": {
                "parent_id": "",
                "thread_id": "",
                "post_id": data.get("id", ""),
            },
            "engagement": {
                "likes": data.get("like_count", 0),
                "replies": data.get("comments_count", 0),
                "shares": 0,
            },
            "metadata": {
                "is_question": self._is_question(data.get("text", "") or data.get("caption", "")),
                "requires_response": self._requires_response(data.get("text", "") or data.get("caption", "")),
                "sentiment": "neutral",
                "topics": [],
            },
        }

        return normalized

    def _make_request(self, url: str, params: Dict, retries: int = 3) -> Dict:
        """Make API request with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {retries} attempts: {e}")
                    raise

        return {}

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> str:
        """Parse Instagram timestamp to ISO-8601"""
        if not timestamp_str:
            return datetime.now().isoformat()

        try:
            if isinstance(timestamp_str, (int, float)):
                dt = datetime.fromtimestamp(timestamp_str)
            else:
                dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
            return dt.isoformat()
        except:
            return timestamp_str if isinstance(timestamp_str, str) else datetime.now().isoformat()

    def _is_question(self, text: str) -> bool:
        """Check if text is a question"""
        if not text:
            return False
        question_words = ["?", "qué", "cuál", "cómo", "cuándo", "dónde", "por qué", "who", "what", "when", "where", "why", "how"]
        return any(word in text.lower() for word in question_words)

    def _requires_response(self, text: str) -> bool:
        """Check if interaction requires a response"""
        return self._is_question(text) or any(
            word in text.lower()
            for word in ["necesito", "quiero", "dame", "envía", "needed", "want", "send", "give"]
        )
