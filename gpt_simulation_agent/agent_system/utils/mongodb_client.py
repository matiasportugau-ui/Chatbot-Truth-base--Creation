"""
MongoDB Client
==============

Client for extracting data from MongoDB collections.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import json
import os


class MongoDBClient:
    """Client for MongoDB data extraction"""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: Optional[str] = None
    ):
        """
        Initialize MongoDB client

        Args:
            connection_string: MongoDB connection string (mongodb://...)
            database_name: Database name
        """
        self.connection_string = connection_string or os.getenv("MONGODB_CONNECTION_STRING")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE_NAME", "panelin")
        self.client = None
        self.db = None
        
        # Try to connect if connection string is provided
        if self.connection_string:
            try:
                from pymongo import MongoClient
                self.client = MongoClient(self.connection_string)
                self.db = self.client[self.database_name]
                logger.info(f"Connected to MongoDB database: {self.database_name}")
            except ImportError:
                logger.warning("pymongo not installed. Install with: pip install pymongo")
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {e}")

    def extract_from_collection(
        self,
        collection_name: str,
        query: Optional[Dict] = None,
        limit: int = 1000,
        since: Optional[datetime] = None,
        projection: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Extract documents from a MongoDB collection

        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
            limit: Maximum number of documents
            since: Extract documents since this date
            projection: Fields to include/exclude

        Returns:
            List of documents
        """
        if not self.db:
            logger.warning("MongoDB not connected. Returning empty list.")
            return []

        try:
            collection = self.db[collection_name]
            
            # Build query
            mongo_query = query or {}
            
            # Add date filter if provided
            if since:
                mongo_query["timestamp"] = {"$gte": since}
            
            # Execute query
            cursor = collection.find(mongo_query, projection).limit(limit)
            documents = list(cursor)
            
            logger.info(f"Extracted {len(documents)} documents from collection: {collection_name}")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting from collection {collection_name}: {e}")
            return []

    def extract_quotes(
        self,
        limit: int = 1000,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Extract quotes from MongoDB

        Args:
            limit: Maximum number of quotes
            since: Extract quotes since this date

        Returns:
            List of quote documents
        """
        # Common collection names for quotes
        collection_names = ["quotes", "cotizaciones", "quotations", "presupuestos"]
        
        all_quotes = []
        
        for collection_name in collection_names:
            try:
                quotes = self.extract_from_collection(
                    collection_name=collection_name,
                    query={},
                    limit=limit,
                    since=since
                )
                all_quotes.extend(quotes)
                
                if quotes:
                    logger.info(f"Found {len(quotes)} quotes in collection: {collection_name}")
                    break  # Use first collection that has data
            except Exception as e:
                logger.debug(f"Collection {collection_name} not found or error: {e}")
                continue
        
        return all_quotes[:limit]  # Limit total results

    def extract_conversations(
        self,
        limit: int = 1000,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Extract conversations from MongoDB

        Args:
            limit: Maximum number of conversations
            since: Extract conversations since this date

        Returns:
            List of conversation documents
        """
        # Common collection names for conversations
        collection_names = [
            "conversations", "conversaciones", "chats", "messages",
            "interactions", "interacciones"
        ]
        
        all_conversations = []
        
        for collection_name in collection_names:
            try:
                conversations = self.extract_from_collection(
                    collection_name=collection_name,
                    query={},
                    limit=limit,
                    since=since
                )
                all_conversations.extend(conversations)
                
                if conversations:
                    logger.info(f"Found {len(conversations)} conversations in collection: {collection_name}")
                    break  # Use first collection that has data
            except Exception as e:
                logger.debug(f"Collection {collection_name} not found or error: {e}")
                continue
        
        return all_conversations[:limit]  # Limit total results

    def extract_social_media(
        self,
        platform: Optional[str] = None,
        limit: int = 1000,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Extract social media interactions from MongoDB

        Args:
            platform: Platform name (facebook, instagram, mercadolibre) or None for all
            limit: Maximum number of interactions
            since: Extract interactions since this date

        Returns:
            List of social media documents
        """
        if platform:
            collection_names = [f"{platform}_interactions", f"{platform}_messages", platform]
        else:
            collection_names = [
                "facebook_interactions", "instagram_interactions", "mercadolibre_interactions",
                "social_media", "redes_sociales"
            ]
        
        all_interactions = []
        
        for collection_name in collection_names:
            try:
                interactions = self.extract_from_collection(
                    collection_name=collection_name,
                    query={"platform": platform} if platform else {},
                    limit=limit,
                    since=since
                )
                all_interactions.extend(interactions)
                
                if interactions:
                    logger.info(f"Found {len(interactions)} interactions in collection: {collection_name}")
            except Exception as e:
                logger.debug(f"Collection {collection_name} not found or error: {e}")
                continue
        
        return all_interactions[:limit]  # Limit total results

    def normalize_document(
        self,
        doc: Dict,
        doc_type: str = "generic"
    ) -> Dict:
        """
        Normalize MongoDB document to unified schema

        Args:
            doc: MongoDB document
            doc_type: Type of document (quote, conversation, social_media)

        Returns:
            Normalized document
        """
        # Convert ObjectId to string if present
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        
        # Normalize timestamp
        timestamp = doc.get("timestamp") or doc.get("created_at") or doc.get("date")
        if timestamp:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
            elif isinstance(timestamp, str):
                try:
                    # Try to parse and re-format
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp = dt.isoformat()
                except:
                    pass
        
        normalized = {
            "id": str(doc.get("_id", doc.get("id", ""))),
            "source": doc_type,
            "platform": doc.get("platform", "mongodb"),
            "timestamp": timestamp or datetime.now().isoformat(),
            "user_query": doc.get("query") or doc.get("message") or doc.get("text") or doc.get("content", ""),
            "chatbot_response": doc.get("response") or doc.get("reply") or doc.get("answer"),
            "metadata": {
                "collection": doc.get("_collection", ""),
                "original_doc": {k: v for k, v in doc.items() if k not in ["_id", "query", "message", "text", "content", "response", "reply", "answer"]}
            }
        }
        
        return normalized

    def list_collections(self) -> List[str]:
        """
        List all collections in the database

        Returns:
            List of collection names
        """
        if not self.db:
            return []
        
        try:
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics for a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection statistics
        """
        if not self.db:
            return {}
        
        try:
            collection = self.db[collection_name]
            count = collection.count_documents({})
            
            # Get date range
            oldest = collection.find_one(sort=[("timestamp", 1)])
            newest = collection.find_one(sort=[("timestamp", -1)])
            
            stats = {
                "collection_name": collection_name,
                "total_documents": count,
                "oldest_document": oldest.get("timestamp") if oldest else None,
                "newest_document": newest.get("timestamp") if newest else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {e}")
            return {}
