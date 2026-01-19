"""
Facebook API Client

Handles Facebook Graph API interactions for ingesting real interactions.
"""

import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from loguru import logger


class FacebookAPIClient:
    """Client for Facebook Graph API"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        page_access_token: Optional[str] = None,
        page_id: Optional[str] = None,
        api_version: str = "v18.0",
    ):
        """
        Initialize Facebook API client

        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            page_access_token: Page Access Token
            page_id: Page ID
            api_version: API version (default: v18.0)
        """
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.page_access_token = page_access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.api_version = api_version or os.getenv("FACEBOOK_API_VERSION", "v18.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        if not self.page_access_token:
            logger.warning("Facebook Page Access Token not provided")

    def get_posts(
        self,
        limit: int = 100,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Get posts from Facebook page

        Args:
            limit: Maximum number of posts to retrieve
            since: Start date
            until: End date

        Returns:
            List of post data
        """
        if not self.page_id or not self.page_access_token:
            raise ValueError("Page ID and Access Token required")

        url = f"{self.base_url}/{self.page_id}/posts"
        params = {
            "access_token": self.page_access_token,
            "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
            "limit": min(limit, 100),
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        posts = []
        try:
            response = self._make_request(url, params)
            posts = response.get("data", [])

            # Handle pagination
            while len(posts) < limit and "paging" in response:
                next_url = response["paging"].get("next")
                if next_url:
                    response = requests.get(next_url).json()
                    posts.extend(response.get("data", []))
                else:
                    break

        except Exception as e:
            logger.error(f"Error fetching Facebook posts: {e}")

        return posts[:limit]

    def get_comments(self, post_id: str, limit: int = 100) -> List[Dict]:
        """
        Get comments for a post

        Args:
            post_id: Post ID
            limit: Maximum number of comments

        Returns:
            List of comment data
        """
        if not self.page_access_token:
            raise ValueError("Page Access Token required")

        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "access_token": self.page_access_token,
            "fields": "id,message,created_time,from,like_count,comment_count",
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
            logger.error(f"Error fetching Facebook comments: {e}")

        return comments[:limit]

    def get_messages(self, limit: int = 100) -> List[Dict]:
        """
        Get messages from Facebook Messenger

        Args:
            limit: Maximum number of messages

        Returns:
            List of message data
        """
        if not self.page_access_token:
            raise ValueError("Page Access Token required")

        url = f"{self.base_url}/me/conversations"
        params = {
            "access_token": self.page_access_token,
            "fields": "id,updated_time",
            "limit": min(limit, 100),
        }

        messages = []
        try:
            response = self._make_request(url, params)
            conversations = response.get("data", [])

            for conv in conversations[:limit]:
                conv_id = conv.get("id")
                if conv_id:
                    # Get messages for conversation
                    msg_url = f"{self.base_url}/{conv_id}/messages"
                    msg_params = {
                        "access_token": self.page_access_token,
                        "fields": "id,message,created_time,from,to",
                        "limit": 50,
                    }
                    msg_response = self._make_request(msg_url, msg_params)
                    messages.extend(msg_response.get("data", []))

        except Exception as e:
            logger.error(f"Error fetching Facebook messages: {e}")

        return messages[:limit]

    def normalize_interaction(self, data: Dict, interaction_type: str) -> Dict:
        """
        Normalize Facebook interaction to unified schema

        Args:
            data: Raw Facebook API data
            interaction_type: Type of interaction (post, comment, message)

        Returns:
            Normalized interaction data
        """
        normalized = {
            "id": data.get("id", ""),
            "platform": "facebook",
            "type": interaction_type,
            "timestamp": self._parse_timestamp(data.get("created_time")),
            "user": {
                "id": data.get("from", {}).get("id", "") if isinstance(data.get("from"), dict) else "",
                "name": data.get("from", {}).get("name", "") if isinstance(data.get("from"), dict) else "",
                "is_business": False,
            },
            "content": data.get("message", ""),
            "context": {
                "parent_id": data.get("parent", {}).get("id", "") if isinstance(data.get("parent"), dict) else "",
                "thread_id": data.get("thread_id", ""),
                "post_id": data.get("post_id", ""),
            },
            "engagement": {
                "likes": data.get("like_count", 0) or data.get("likes", {}).get("summary", {}).get("total_count", 0),
                "replies": data.get("comment_count", 0),
                "shares": data.get("shares", {}).get("count", 0) if isinstance(data.get("shares"), dict) else 0,
            },
            "metadata": {
                "is_question": self._is_question(data.get("message", "")),
                "requires_response": self._requires_response(data.get("message", "")),
                "sentiment": "neutral",  # Could be enhanced with sentiment analysis
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
        """Parse Facebook timestamp to ISO-8601"""
        if not timestamp_str:
            return datetime.now().isoformat()

        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
            return dt.isoformat()
        except:
            return timestamp_str

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
