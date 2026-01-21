"""
Multi-Level Training System
============================

Four levels of training for knowledge base evolution:

Level 1: Static Grounding (Documentation & Quotes)
- Converts existing PDFs, manuals, quotes into searchable KB
- Forms the "source of truth" foundation

Level 2: Interaction-Driven Evolution (Customer Support)
- Uses real-world chat transcripts and service interactions
- Creates ground truth pairs for evaluation
- Identifies leaks where KB fails

Level 3: Proactive Social & Synthetic Ingestion
- Monitors social networks and feedback loops
- Generates synthetic test cases
- Updates KB with emerging trends

Level 4: Autonomous Agent Feedback Loop
- Specialized agents monitor and update KB autonomously
- Continuous improvement based on performance metrics
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import re
from loguru import logger

from gpt_simulation_agent.agent_system.agent_training_processor import TrainingProcessor
from gpt_simulation_agent.agent_system.utils.analytics_engine import AnalyticsEngine


@dataclass
class TrainingResult:
    """Result of training operation"""
    level: int
    timestamp: str
    items_processed: int
    items_added: int
    items_updated: int
    items_failed: int
    kb_changes: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class Level1StaticGrounding:
    """
    Level 1: Static Grounding
    Converts existing documentation, quotes, and PDFs into structured KB.
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        quotes_path: Optional[str] = None,
        pdfs_path: Optional[str] = None
    ):
        """
        Initialize Level 1 trainer
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            quotes_path: Path to quotes directory
            pdfs_path: Path to PDFs directory
        """
        self.kb_path = Path(knowledge_base_path)
        self.quotes_path = Path(quotes_path) if quotes_path else None
        self.pdfs_path = Path(pdfs_path) if pdfs_path else None
    
    def train_from_quotes(
        self,
        quotes: List[Dict[str, Any]],
        target_kb_file: str = "BMC_Base_Conocimiento_GPT.json"
    ) -> TrainingResult:
        """
        Train KB from quote analysis
        
        Args:
            quotes: List of quote dictionaries
            target_kb_file: Target KB file to update
            
        Returns:
            TrainingResult with changes made
        """
        logger.info(f"Level 1: Training from {len(quotes)} quotes")
        
        result = TrainingResult(
            level=1,
            timestamp=datetime.now().isoformat(),
            items_processed=len(quotes),
            items_added=0,
            items_updated=0,
            items_failed=0
        )
        
        kb_file = self.kb_path / target_kb_file
        
        if not kb_file.exists():
            logger.warning(f"KB file not found: {kb_file}")
            result.items_failed = len(quotes)
            return result
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading KB: {e}")
            result.items_failed = len(quotes)
            return result
        
        changes = []
        
        for quote in quotes:
            try:
                # Extract product information from quote
                product_info = self._extract_product_info(quote)
                
                # Extract pricing information
                pricing_info = self._extract_pricing_info(quote)
                
                # Extract technical specifications
                specs = self._extract_specifications(quote)
                
                # Update KB
                kb_changes = self._update_kb_with_quote_data(
                    kb_data, product_info, pricing_info, specs
                )
                
                if kb_changes:
                    changes.extend(kb_changes)
                    result.items_added += len([c for c in kb_changes if c.get("action") == "add"])
                    result.items_updated += len([c for c in kb_changes if c.get("action") == "update"])
            
            except Exception as e:
                logger.error(f"Error processing quote: {e}")
                result.items_failed += 1
        
        result.kb_changes = changes
        result.recommendations = self._generate_level1_recommendations(changes)
        
        # Save updated KB
        if changes:
            try:
                with open(kb_file, 'w', encoding='utf-8') as f:
                    json.dump(kb_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Updated KB file: {kb_file}")
            except Exception as e:
                logger.error(f"Error saving KB: {e}")
        
        return result
    
    def _extract_product_info(self, quote: Dict) -> Dict:
        """Extract product information from quote"""
        product_info = {}
        
        # Look for product names
        quote_text = json.dumps(quote).lower()
        
        products = ["isodec", "isoroof", "isopanel", "isowall"]
        for product in products:
            if product in quote_text:
                product_info["product_name"] = product.upper()
                break
        
        # Extract product code if available
        if "product_code" in quote:
            product_info["product_code"] = quote["product_code"]
        
        return product_info
    
    def _extract_pricing_info(self, quote: Dict) -> Dict:
        """Extract pricing information from quote"""
        pricing = {}
        
        # Look for price fields
        price_fields = ["price", "precio", "total", "subtotal", "costo"]
        for field in price_fields:
            if field in quote:
                pricing[field] = quote[field]
        
        # Extract currency
        if "currency" in quote:
            pricing["currency"] = quote["currency"]
        elif "$" in str(quote):
            pricing["currency"] = "USD"
        
        return pricing
    
    def _extract_specifications(self, quote: Dict) -> Dict:
        """Extract technical specifications from quote"""
        specs = {}
        
        # Look for thickness/espesor
        thickness_fields = ["thickness", "espesor", "grosor"]
        for field in thickness_fields:
            if field in quote:
                specs["thickness"] = quote[field]
        
        # Look for dimensions
        dimension_fields = ["width", "ancho", "length", "largo", "height", "alto"]
        for field in dimension_fields:
            if field in quote:
                specs[field] = quote[field]
        
        return specs
    
    def _update_kb_with_quote_data(
        self,
        kb_data: Dict,
        product_info: Dict,
        pricing_info: Dict,
        specs: Dict
    ) -> List[Dict]:
        """Update KB with quote data"""
        changes = []
        
        # Ensure products structure exists
        if "products" not in kb_data:
            kb_data["products"] = {}
        
        product_name = product_info.get("product_name")
        if not product_name:
            return changes
        
        # Initialize product entry if needed
        if product_name not in kb_data["products"]:
            kb_data["products"][product_name] = {}
            changes.append({
                "action": "add",
                "type": "product",
                "product": product_name,
                "description": "Added from quote analysis"
            })
        
        # Update pricing
        if pricing_info:
            if "pricing" not in kb_data["products"][product_name]:
                kb_data["products"][product_name]["pricing"] = {}
            
            for key, value in pricing_info.items():
                if key not in kb_data["products"][product_name]["pricing"]:
                    kb_data["products"][product_name]["pricing"][key] = value
                    changes.append({
                        "action": "add",
                        "type": "pricing",
                        "product": product_name,
                        "field": key,
                        "value": value
                    })
                elif kb_data["products"][product_name]["pricing"][key] != value:
                    changes.append({
                        "action": "update",
                        "type": "pricing",
                        "product": product_name,
                        "field": key,
                        "old_value": kb_data["products"][product_name]["pricing"][key],
                        "new_value": value
                    })
                    kb_data["products"][product_name]["pricing"][key] = value
        
        # Update specifications
        if specs:
            if "specifications" not in kb_data["products"][product_name]:
                kb_data["products"][product_name]["specifications"] = {}
            
            for key, value in specs.items():
                if key not in kb_data["products"][product_name]["specifications"]:
                    kb_data["products"][product_name]["specifications"][key] = value
                    changes.append({
                        "action": "add",
                        "type": "specification",
                        "product": product_name,
                        "field": key,
                        "value": value
                    })
        
        return changes
    
    def _generate_level1_recommendations(self, changes: List[Dict]) -> List[str]:
        """Generate recommendations from Level 1 training"""
        recommendations = []
        
        if not changes:
            recommendations.append("No changes made. Verify quote data format.")
            return recommendations
        
        products_added = len([c for c in changes if c.get("type") == "product" and c.get("action") == "add"])
        if products_added > 0:
            recommendations.append(
                f"{products_added} new products added. Review and validate product information."
            )
        
        pricing_updates = len([c for c in changes if c.get("type") == "pricing"])
        if pricing_updates > 0:
            recommendations.append(
                f"{pricing_updates} pricing updates. Verify prices against master source."
            )
        
        return recommendations


class Level2InteractionEvolution:
    """
    Level 2: Interaction-Driven Evolution
    Uses customer support interactions to evolve KB.
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        interactions_path: Optional[str] = None
    ):
        """
        Initialize Level 2 trainer
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            interactions_path: Path to interactions directory
        """
        self.kb_path = Path(knowledge_base_path)
        self.interactions_path = Path(interactions_path) if interactions_path else Path("training_data/interactions")
        self.analytics_engine = AnalyticsEngine(str(self.interactions_path))
    
    def train_from_interactions(
        self,
        interactions: List[Dict[str, Any]],
        target_kb_file: str = "BMC_Base_Conocimiento_GPT.json"
    ) -> TrainingResult:
        """
        Train KB from customer interactions
        
        Args:
            interactions: List of interaction dictionaries
            target_kb_file: Target KB file to update
            
        Returns:
            TrainingResult with changes made
        """
        logger.info(f"Level 2: Training from {len(interactions)} interactions")
        
        result = TrainingResult(
            level=2,
            timestamp=datetime.now().isoformat(),
            items_processed=len(interactions),
            items_added=0,
            items_updated=0,
            items_failed=0
        )
        
        # Analyze interactions
        analysis = self.analytics_engine.analyze_interactions(interactions)
        
        # Extract patterns
        patterns = self._extract_interaction_patterns(interactions, analysis)
        
        # Identify knowledge gaps
        gaps = self._identify_knowledge_gaps(interactions)
        
        # Update KB with patterns and gap fills
        kb_file = self.kb_path / target_kb_file
        if kb_file.exists():
            changes = self._update_kb_with_interactions(
                kb_file, patterns, gaps, interactions
            )
            result.kb_changes = changes
            result.items_added = len([c for c in changes if c.get("action") == "add"])
            result.items_updated = len([c for c in changes if c.get("action") == "update"])
        
        result.metrics = {
            "common_queries": analysis.get("common_queries", []),
            "question_rate": analysis.get("question_rate", 0),
            "patterns_identified": len(patterns),
            "gaps_identified": len(gaps)
        }
        
        result.recommendations = self._generate_level2_recommendations(patterns, gaps)
        
        return result
    
    def _extract_interaction_patterns(
        self,
        interactions: List[Dict],
        analysis: Dict
    ) -> List[Dict]:
        """Extract patterns from interactions"""
        patterns = []
        
        # Common queries pattern
        common_queries = analysis.get("common_queries", [])
        for query_info in common_queries:
            patterns.append({
                "type": "common_query",
                "query": query_info.get("query", ""),
                "frequency": query_info.get("count", 0),
                "suggestion": "Add to FAQ or KB documentation"
            })
        
        return patterns
    
    def _identify_knowledge_gaps(self, interactions: List[Dict]) -> List[Dict]:
        """Identify knowledge gaps from interactions"""
        gaps = []
        
        for interaction in interactions:
            response = interaction.get("response", "").lower()
            
            # Check for "I don't know" patterns
            if any(phrase in response for phrase in [
                "no tengo", "no sé", "no disponible", "no encuentro"
            ]):
                gaps.append({
                    "query": interaction.get("query", ""),
                    "response": interaction.get("response", ""),
                    "gap_type": "missing_information",
                    "category": self._categorize_gap(interaction.get("query", ""))
                })
        
        return gaps
    
    def _categorize_gap(self, query: str) -> str:
        """Categorize knowledge gap"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["precio", "costo"]):
            return "pricing"
        elif any(kw in query_lower for kw in ["espesor", "autoportancia"]):
            return "specifications"
        elif any(kw in query_lower for kw in ["fórmula", "calcular"]):
            return "formulas"
        else:
            return "general"
    
    def _update_kb_with_interactions(
        self,
        kb_file: Path,
        patterns: List[Dict],
        gaps: List[Dict],
        interactions: List[Dict]
    ) -> List[Dict]:
        """Update KB with interaction data"""
        changes = []
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading KB: {e}")
            return changes
        
        # Add FAQ section if gaps found
        if gaps:
            if "faq" not in kb_data:
                kb_data["faq"] = []
            
            for gap in gaps[:10]:  # Top 10 gaps
                faq_entry = {
                    "question": gap["query"],
                    "answer": "Information to be added",
                    "category": gap["category"],
                    "source": "interaction_analysis",
                    "added_at": datetime.now().isoformat()
                }
                kb_data["faq"].append(faq_entry)
                changes.append({
                    "action": "add",
                    "type": "faq",
                    "question": gap["query"],
                    "category": gap["category"]
                })
        
        # Save updated KB
        if changes:
            try:
                with open(kb_file, 'w', encoding='utf-8') as f:
                    json.dump(kb_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error saving KB: {e}")
        
        return changes
    
    def _generate_level2_recommendations(
        self,
        patterns: List[Dict],
        gaps: List[Dict]
    ) -> List[str]:
        """Generate recommendations from Level 2 training"""
        recommendations = []
        
        if gaps:
            categories = {}
            for gap in gaps:
                cat = gap.get("category", "general")
                categories[cat] = categories.get(cat, 0) + 1
            
            top_category = max(categories.items(), key=lambda x: x[1])
            recommendations.append(
                f"Add {top_category[0]} information to KB. "
                f"{top_category[1]} gaps identified in this category."
            )
        
        if patterns:
            recommendations.append(
                f"{len(patterns)} interaction patterns identified. "
                "Consider adding common queries to FAQ section."
            )
        
        return recommendations


class Level3SocialIngestion:
    """
    Level 3: Proactive Social & Synthetic Ingestion
    Monitors social networks and generates synthetic test cases.
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        social_data_path: Optional[str] = None
    ):
        """
        Initialize Level 3 trainer
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            social_data_path: Path to social media data
        """
        self.kb_path = Path(knowledge_base_path)
        self.social_data_path = Path(social_data_path) if social_data_path else Path("training_data/social_media")
        self.training_processor = TrainingProcessor(str(self.social_data_path))
    
    def train_from_social_media(
        self,
        social_interactions: List[Dict[str, Any]],
        target_kb_file: str = "BMC_Base_Conocimiento_GPT.json"
    ) -> TrainingResult:
        """
        Train KB from social media interactions
        
        Args:
            social_interactions: List of social media interactions
            target_kb_file: Target KB file to update
            
        Returns:
            TrainingResult with changes made
        """
        logger.info(f"Level 3: Training from {len(social_interactions)} social interactions")
        
        result = TrainingResult(
            level=3,
            timestamp=datetime.now().isoformat(),
            items_processed=len(social_interactions),
            items_added=0,
            items_updated=0,
            items_failed=0
        )
        
        # Process social media data
        processed = self.training_processor.process_all()
        
        # Extract trends and sentiment
        trends = self._extract_trends(social_interactions)
        
        # Generate synthetic test cases
        synthetic_cases = self._generate_synthetic_cases(social_interactions, trends)
        
        # Update KB with trends
        kb_file = self.kb_path / target_kb_file
        if kb_file.exists():
            changes = self._update_kb_with_trends(kb_file, trends, synthetic_cases)
            result.kb_changes = changes
            result.items_added = len([c for c in changes if c.get("action") == "add"])
            result.items_updated = len([c for c in changes if c.get("action") == "update"])
        
        result.metrics = {
            "trends_identified": len(trends),
            "synthetic_cases_generated": len(synthetic_cases),
            "platforms": list(set(i.get("platform", "unknown") for i in social_interactions))
        }
        
        result.recommendations = self._generate_level3_recommendations(trends)
        
        return result
    
    def _extract_trends(self, interactions: List[Dict]) -> List[Dict]:
        """Extract trends from social media interactions"""
        trends = []
        
        # Group by topic/keyword
        topic_counter = {}
        for interaction in interactions:
            content = interaction.get("content", "").lower()
            
            # Extract topics
            topics = ["precio", "producto", "cotización", "espesor", "autoportancia"]
            for topic in topics:
                if topic in content:
                    topic_counter[topic] = topic_counter.get(topic, 0) + 1
        
        # Create trend entries
        for topic, count in topic_counter.items():
            if count >= 3:  # Minimum threshold
                trends.append({
                    "topic": topic,
                    "frequency": count,
                    "trend_type": "emerging" if count < 10 else "established"
                })
        
        return trends
    
    def _generate_synthetic_cases(
        self,
        interactions: List[Dict],
        trends: List[Dict]
    ) -> List[Dict]:
        """Generate synthetic test cases from social interactions"""
        cases = []
        
        # Create test cases based on trends
        for trend in trends:
            cases.append({
                "query": f"Consulta sobre {trend['topic']}",
                "expected_category": trend["topic"],
                "synthetic": True,
                "source": "social_trend_analysis"
            })
        
        return cases
    
    def _update_kb_with_trends(
        self,
        kb_file: Path,
        trends: List[Dict],
        synthetic_cases: List[Dict]
    ) -> List[Dict]:
        """Update KB with social media trends"""
        changes = []
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading KB: {e}")
            return changes
        
        # Add trends metadata
        if "trends" not in kb_data:
            kb_data["trends"] = []
        
        for trend in trends:
            kb_data["trends"].append({
                **trend,
                "updated_at": datetime.now().isoformat()
            })
            changes.append({
                "action": "add",
                "type": "trend",
                "topic": trend["topic"]
            })
        
        # Save updated KB
        if changes:
            try:
                with open(kb_file, 'w', encoding='utf-8') as f:
                    json.dump(kb_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error saving KB: {e}")
        
        return changes
    
    def _generate_level3_recommendations(self, trends: List[Dict]) -> List[str]:
        """Generate recommendations from Level 3 training"""
        recommendations = []
        
        if trends:
            established = [t for t in trends if t.get("trend_type") == "established"]
            if established:
                recommendations.append(
                    f"{len(established)} established trends identified. "
                    "Consider adding dedicated sections in KB."
                )
        
        return recommendations


class Level4AutonomousFeedback:
    """
    Level 4: Autonomous Agent Feedback Loop
    Continuous improvement based on performance metrics.
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        evaluation_results_path: Optional[str] = None
    ):
        """
        Initialize Level 4 trainer
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            evaluation_results_path: Path to evaluation results
        """
        self.kb_path = Path(knowledge_base_path)
        self.eval_results_path = Path(evaluation_results_path) if evaluation_results_path else Path("kb_training_system/evaluation_results")
        self.eval_results_path.mkdir(parents=True, exist_ok=True)
    
    def train_from_evaluation(
        self,
        evaluation_results: List[Dict[str, Any]],
        target_kb_file: str = "BMC_Base_Conocimiento_GPT.json"
    ) -> TrainingResult:
        """
        Train KB from evaluation results (autonomous feedback)
        
        Args:
            evaluation_results: List of evaluation results
            target_kb_file: Target KB file to update
            
        Returns:
            TrainingResult with changes made
        """
        logger.info(f"Level 4: Training from {len(evaluation_results)} evaluation results")
        
        result = TrainingResult(
            level=4,
            timestamp=datetime.now().isoformat(),
            items_processed=len(evaluation_results),
            items_added=0,
            items_updated=0,
            items_failed=0
        )
        
        # Analyze evaluation results
        performance_metrics = self._analyze_performance(evaluation_results)
        
        # Identify improvement areas
        improvements = self._identify_improvements(evaluation_results, performance_metrics)
        
        # Update KB autonomously
        kb_file = self.kb_path / target_kb_file
        if kb_file.exists():
            changes = self._apply_autonomous_updates(kb_file, improvements)
            result.kb_changes = changes
            result.items_added = len([c for c in changes if c.get("action") == "add"])
            result.items_updated = len([c for c in changes if c.get("action") == "update"])
        
        result.metrics = performance_metrics
        result.recommendations = self._generate_level4_recommendations(improvements)
        
        return result
    
    def _analyze_performance(self, results: List[Dict]) -> Dict:
        """Analyze performance metrics from evaluation results"""
        if not results:
            return {}
        
        avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results)
        avg_groundedness = sum(r.get("groundedness_score", 0) for r in results) / len(results)
        avg_coherence = sum(r.get("coherence_score", 0) for r in results) / len(results)
        
        return {
            "average_relevance": avg_relevance,
            "average_groundedness": avg_groundedness,
            "average_coherence": avg_coherence,
            "total_evaluations": len(results)
        }
    
    def _identify_improvements(
        self,
        results: List[Dict],
        metrics: Dict
    ) -> List[Dict]:
        """Identify areas for improvement"""
        improvements = []
        
        # Low relevance improvements
        if metrics.get("average_relevance", 1.0) < 0.7:
            improvements.append({
                "type": "relevance",
                "priority": "high",
                "action": "improve_query_matching",
                "description": "Enhance KB with synonyms and alternative phrasings"
            })
        
        # Low groundedness improvements
        if metrics.get("average_groundedness", 1.0) < 0.6:
            improvements.append({
                "type": "groundedness",
                "priority": "high",
                "action": "strengthen_source_citations",
                "description": "Ensure responses cite specific KB sources"
            })
        
        return improvements
    
    def _apply_autonomous_updates(
        self,
        kb_file: Path,
        improvements: List[Dict]
    ) -> List[Dict]:
        """Apply autonomous updates to KB"""
        changes = []
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading KB: {e}")
            return changes
        
        # Apply improvements
        for improvement in improvements:
            if improvement["type"] == "relevance":
                # Add synonyms section
                if "synonyms" not in kb_data:
                    kb_data["synonyms"] = {}
                    changes.append({
                        "action": "add",
                        "type": "metadata",
                        "field": "synonyms",
                        "description": "Added for improved query matching"
                    })
            
            elif improvement["type"] == "groundedness":
                # Add source citation guidelines
                if "citation_guidelines" not in kb_data:
                    kb_data["citation_guidelines"] = {
                        "always_cite_sources": True,
                        "preferred_source_level": 1
                    }
                    changes.append({
                        "action": "add",
                        "type": "metadata",
                        "field": "citation_guidelines"
                    })
        
        # Save updated KB
        if changes:
            try:
                with open(kb_file, 'w', encoding='utf-8') as f:
                    json.dump(kb_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error saving KB: {e}")
        
        return changes
    
    def _generate_level4_recommendations(self, improvements: List[Dict]) -> List[str]:
        """Generate recommendations from Level 4 training"""
        recommendations = []
        
        high_priority = [i for i in improvements if i.get("priority") == "high"]
        if high_priority:
            recommendations.append(
                f"{len(high_priority)} high-priority improvements identified. "
                "Consider immediate KB updates."
            )
        
        return recommendations
