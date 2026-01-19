"""
Social Media Ingestion Engine

Ingests real interactions from Facebook and Instagram.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from .utils.facebook_api import FacebookAPIClient
from .utils.instagram_api import InstagramAPIClient


class SocialIngestionEngine:
    """Engine for ingesting social media interactions"""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        facebook_client: Optional[FacebookAPIClient] = None,
        instagram_client: Optional[InstagramAPIClient] = None,
    ):
        """
        Initialize social ingestion engine

        Args:
            output_dir: Directory to save ingested data
            facebook_client: Facebook API client (optional)
            instagram_client: Instagram API client (optional)
        """
        self.output_dir = Path(output_dir) if output_dir else Path("training_data/social_media")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.facebook_client = facebook_client or FacebookAPIClient()
        self.instagram_client = instagram_client or InstagramAPIClient()

    def ingest(
        self,
        platforms: List[str] = ["facebook", "instagram"],
        days_back: int = 30,
        limit_per_platform: int = 1000,
    ) -> Dict:
        """
        Ingest interactions from specified platforms

        Args:
            platforms: List of platforms to ingest from
            days_back: Number of days to look back
            limit_per_platform: Maximum interactions per platform

        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Starting social media ingestion from {platforms}")

        since_date = datetime.now() - timedelta(days=days_back)
        results = {
            "facebook": {"count": 0, "files": []},
            "instagram": {"count": 0, "files": []},
        }

        if "facebook" in platforms:
            fb_results = self._ingest_facebook(since_date, limit_per_platform)
            results["facebook"] = fb_results

        if "instagram" in platforms:
            ig_results = self._ingest_instagram(since_date, limit_per_platform)
            results["instagram"] = ig_results

        total_count = results["facebook"]["count"] + results["instagram"]["count"]
        logger.info(f"Ingestion completed. Total interactions: {total_count}")

        return results

    def _ingest_facebook(
        self, since_date: datetime, limit: int
    ) -> Dict:
        """Ingest Facebook interactions"""
        results = {"count": 0, "files": []}

        try:
            # Get posts
            posts = self.facebook_client.get_posts(limit=limit, since=since_date)
            logger.info(f"Fetched {len(posts)} Facebook posts")

            # Normalize and save posts
            normalized_posts = []
            for post in posts:
                normalized = self.facebook_client.normalize_interaction(post, "post")
                normalized_posts.append(normalized)

            if normalized_posts:
                self._save_interactions(normalized_posts, "facebook", "posts")
                results["files"].append("facebook/posts")
                results["count"] += len(normalized_posts)

            # Get comments for each post
            all_comments = []
            for post in posts[:50]:  # Limit to avoid too many API calls
                post_id = post.get("id")
                if post_id:
                    comments = self.facebook_client.get_comments(post_id, limit=100)
                    for comment in comments:
                        normalized = self.facebook_client.normalize_interaction(comment, "comment")
                        normalized["context"]["post_id"] = post_id
                        all_comments.append(normalized)

            if all_comments:
                self._save_interactions(all_comments, "facebook", "comments")
                results["files"].append("facebook/comments")
                results["count"] += len(all_comments)

            # Get messages
            messages = self.facebook_client.get_messages(limit=min(limit, 500))
            normalized_messages = [
                self.facebook_client.normalize_interaction(msg, "message")
                for msg in messages
            ]

            if normalized_messages:
                self._save_interactions(normalized_messages, "facebook", "messages")
                results["files"].append("facebook/messages")
                results["count"] += len(normalized_messages)

        except Exception as e:
            logger.error(f"Error ingesting Facebook data: {e}")

        return results

    def _ingest_instagram(
        self, since_date: datetime, limit: int
    ) -> Dict:
        """Ingest Instagram interactions"""
        results = {"count": 0, "files": []}

        try:
            # Get media posts
            media = self.instagram_client.get_media(limit=limit, since=since_date)
            logger.info(f"Fetched {len(media)} Instagram posts")

            # Normalize and save posts
            normalized_posts = []
            for post in media:
                normalized = self.instagram_client.normalize_interaction(post, "post")
                normalized_posts.append(normalized)

            if normalized_posts:
                self._save_interactions(normalized_posts, "instagram", "posts")
                results["files"].append("instagram/posts")
                results["count"] += len(normalized_posts)

            # Get comments for each post
            all_comments = []
            for post in media[:50]:  # Limit to avoid too many API calls
                media_id = post.get("id")
                if media_id:
                    comments = self.instagram_client.get_comments(media_id, limit=100)
                    for comment in comments:
                        normalized = self.instagram_client.normalize_interaction(comment, "comment")
                        normalized["context"]["post_id"] = media_id
                        all_comments.append(normalized)

            if all_comments:
                self._save_interactions(all_comments, "instagram", "comments")
                results["files"].append("instagram/comments")
                results["count"] += len(all_comments)

            # DMs require special setup
            dms = self.instagram_client.get_direct_messages(limit=100)
            if dms:
                normalized_dms = [
                    self.instagram_client.normalize_interaction(dm, "dm")
                    for dm in dms
                ]
                self._save_interactions(normalized_dms, "instagram", "dms")
                results["files"].append("instagram/dms")
                results["count"] += len(normalized_dms)

        except Exception as e:
            logger.error(f"Error ingesting Instagram data: {e}")

        return results

    def _save_interactions(
        self, interactions: List[Dict], platform: str, interaction_type: str
    ):
        """Save interactions to file"""
        save_dir = self.output_dir / platform / interaction_type
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{interaction_type}_{timestamp}.json"

        filepath = save_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(interactions, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(interactions)} {platform} {interaction_type} to {filepath}")
