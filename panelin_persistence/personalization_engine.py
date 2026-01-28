#!/usr/bin/env python3
"""
Personalization Engine
======================

Personalizes bot responses based on user profiles, preferences,
and interaction history.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from collections import Counter

from .user_profiles import UserProfileDatabase


class PersonalizationEngine:
    """Personalizes bot behavior based on user data"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize personalization engine
        
        Args:
            db_path: Path to user profiles database
        """
        self.db = UserProfileDatabase(db_path)
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized context for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            User context with preferences, history, and personalization data
        """
        user = self.db.get_user(user_id)
        if not user:
            # Create new user on first interaction
            user = self.db.create_or_update_user(user_id)
        
        # Parse JSON fields
        preferences = json.loads(user.preferences)
        learning_patterns = json.loads(user.learning_patterns)
        metadata = json.loads(user.metadata)
        
        # Get recent interactions
        recent_interactions = self.db.get_user_interactions(user_id, limit=20)
        
        # Analyze patterns
        interaction_summary = self._analyze_interaction_patterns(recent_interactions)
        
        return {
            "user_id": user_id,
            "name": user.name,
            "preferences": preferences,
            "interaction_count": user.interaction_count,
            "first_interaction": user.first_interaction,
            "last_interaction": user.last_interaction,
            "learning_patterns": learning_patterns,
            "metadata": metadata,
            "interaction_summary": interaction_summary,
            "personalization_level": self._calculate_personalization_level(user.interaction_count)
        }
    
    def _analyze_interaction_patterns(
        self,
        interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        if not interactions:
            return {
                "total": 0,
                "common_types": [],
                "recent_trend": "new_user"
            }
        
        # Count interaction types
        interaction_types = [i["interaction_type"] for i in interactions]
        type_counts = Counter(interaction_types)
        
        return {
            "total": len(interactions),
            "common_types": [
                {"type": t, "count": c} 
                for t, c in type_counts.most_common(5)
            ],
            "recent_trend": self._calculate_trend(interactions)
        }
    
    def _calculate_trend(self, interactions: List[Dict[str, Any]]) -> str:
        """Calculate user engagement trend"""
        if len(interactions) < 5:
            return "new_user"
        
        # Compare recent vs older interactions
        recent_count = len([i for i in interactions[:10]])
        older_count = len([i for i in interactions[10:20]]) if len(interactions) > 10 else 0
        
        if older_count == 0:
            return "new_user"
        elif recent_count > older_count * 1.2:
            return "increasing"
        elif recent_count < older_count * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_personalization_level(self, interaction_count: int) -> str:
        """Calculate personalization level based on interaction count"""
        if interaction_count == 0:
            return "none"
        elif interaction_count < 5:
            return "minimal"
        elif interaction_count < 20:
            return "moderate"
        elif interaction_count < 50:
            return "high"
        else:
            return "advanced"
    
    def update_user_learning(
        self,
        user_id: str,
        learning_data: Dict[str, Any]
    ):
        """Update user learning patterns"""
        user = self.db.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get current learning patterns
        current_patterns = json.loads(user.learning_patterns)
        
        # Merge new learning data
        for key, value in learning_data.items():
            if key in current_patterns:
                # Aggregate learning data
                if isinstance(value, (int, float)) and isinstance(current_patterns[key], (int, float)):
                    current_patterns[key] = (current_patterns[key] + value) / 2
                else:
                    current_patterns[key] = value
            else:
                current_patterns[key] = value
        
        # Update in database
        cursor = self.db.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET learning_patterns = ?, updated_at = ?
            WHERE user_id = ?
        """, (
            json.dumps(current_patterns, ensure_ascii=False),
            datetime.now().isoformat(),
            user_id
        ))
        
        self.db.conn.commit()
    
    def get_personalized_recommendations(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User identifier
            context: Current conversation context
        
        Returns:
            List of personalized recommendations
        """
        user_context = self.get_user_context(user_id)
        preferences = user_context["preferences"]
        interaction_summary = user_context["interaction_summary"]
        
        recommendations = []
        
        # Recommend based on preferences
        if preferences.get("preferred_products"):
            recommendations.append({
                "type": "product_preference",
                "message": f"Based on your preferences, you might be interested in {preferences['preferred_products']}",
                "confidence": 0.8
            })
        
        # Recommend based on interaction patterns
        common_types = interaction_summary.get("common_types", [])
        if common_types:
            top_type = common_types[0]["type"]
            recommendations.append({
                "type": "interaction_pattern",
                "message": f"You frequently ask about {top_type}. Would you like more information?",
                "confidence": 0.7
            })
        
        # Recommend based on engagement trend
        trend = interaction_summary.get("recent_trend")
        if trend == "increasing":
            recommendations.append({
                "type": "engagement",
                "message": "You're engaging more frequently. Consider setting up automated reports.",
                "confidence": 0.6
            })
        
        return recommendations
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
