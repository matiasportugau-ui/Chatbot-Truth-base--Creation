#!/usr/bin/env python3
"""
Agente Integrador de Conocimiento Revisado en Conversaciones
============================================================

Agente que:
1. Revisa conversaciones desde múltiples fuentes (MongoDB, CSV, JSON, SQLite)
2. Valida conocimiento usando métricas de evaluación
3. Extrae conocimiento validado
4. Integra conocimiento en Knowledge Base siguiendo jerarquía de Source of Truth
"""

import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
import sys

# Importar componentes existentes
sys.path.insert(0, str(Path(__file__).parent))

try:
    from kb_training_system.kb_evaluator import KnowledgeBaseEvaluator
    from kb_training_system.kb_leak_detector import KnowledgeBaseLeakDetector
    from panelin_improvements.source_of_truth_validator import (
        SourceOfTruthValidator
    )
    from gpt_simulation_agent.agent_system.utils.mongodb_client import (
        MongoDBClient
    )
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    KnowledgeBaseEvaluator = None  # type: ignore
    KnowledgeBaseLeakDetector = None  # type: ignore
    SourceOfTruthValidator = None  # type: ignore
    MongoDBClient = None  # type: ignore


@dataclass
class ConversationRecord:
    """Registro de conversación normalizado"""
    id: str
    source: str  # 'mongodb', 'csv', 'json', 'sqlite', 'social'
    platform: str
    timestamp: str
    user_query: str
    chatbot_response: Optional[str] = None
    sources_consulted: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    quality_scores: Dict = field(default_factory=dict)
    knowledge_extracted: Dict = field(default_factory=dict)


@dataclass
class KnowledgeItem:
    """Item de conocimiento extraído"""
    type: str  # 'product', 'price', 'formula', 'faq', 'correction', 'rule'
    content: Dict
    confidence: float
    source_conversation: str
    validation_status: str  # 'approved', 'pending', 'rejected'
    conflicts: List[str] = field(default_factory=list)


@dataclass
class IntegrationReport:
    """Reporte de integración"""
    timestamp: str
    conversations_reviewed: int
    knowledge_extracted: Dict[str, int]
    integration_results: Dict[str, int]
    quality_scores: Dict[str, float]
    conflicts_detected: int
    recommendations: List[str]
    changes: List[Dict]


class AgenteIntegradorConocimiento:
    """Agente principal de integración de conocimiento"""

    def __init__(
        self,
        kb_path: str = "./gpt_configs",
        training_data_path: str = "./training_data",
        output_path: str = "./integration_output",
        db_path: str = "ingestion_database.db"
    ):
        """
        Inicializar agente

        Args:
            kb_path: Ruta a directorio de Knowledge Base
            training_data_path: Ruta a directorio de datos de entrenamiento
            output_path: Ruta para reportes de salida
            db_path: Ruta a base de datos SQLite
        """
        self.kb_path = Path(kb_path)
        self.training_data_path = Path(training_data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        self.db_path = db_path

        # Inicializar componentes
        if MongoDBClient:
            self.mongodb_client = MongoDBClient()
        else:
            self.mongodb_client = None

        if KnowledgeBaseEvaluator:
            self.evaluator = KnowledgeBaseEvaluator(str(self.kb_path))
        else:
            self.evaluator = None

        if KnowledgeBaseLeakDetector:
            self.leak_detector = KnowledgeBaseLeakDetector(
                str(self.kb_path)
            )
        else:
            self.leak_detector = None

        if SourceOfTruthValidator:
            self.source_validator = SourceOfTruthValidator(
                str(self.kb_path)
            )
        else:
            self.source_validator = None

        # Umbrales de validación
        self.min_relevance = 0.8
        self.min_groundedness = 0.8
        self.min_coherence = 0.8
        self.min_confidence = 0.8

        # Jerarquía de KB
        self.kb_hierarchy = {
            "level_1": ["BMC_Base_Conocimiento_GPT-2.json", "BMC_Base_Conocimiento_GPT.json"],
            "level_2": ["BMC_Base_Unificada_v4.json"],
            "level_3": ["panelin_truth_bmcuruguay_web_only_v2.json"],
            "level_4": ["panelin_context_consolidacion_sin_backend.md", "Aleros.rtf"]
        }

    def review_conversations(
        self,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[ConversationRecord]:
        """
        Revisar conversaciones desde todas las fuentes

        Args:
            since: Fecha desde la cual revisar (opcional)
            limit: Límite de conversaciones por fuente

        Returns:
            Lista de conversaciones normalizadas
        """
        conversations = []

        # 1. MongoDB
        if self.mongodb_client and self.mongodb_client.db:
            print("📊 Extrayendo conversaciones de MongoDB...")
            mongo_conversations = self.mongodb_client.extract_conversations(
                limit=limit,
                since=since
            )
            for conv in mongo_conversations:
                normalized = self.mongodb_client.normalize_document(conv, "conversation")
                conversations.append(self._create_conversation_record(normalized, "mongodb"))

        # 2. SQLite
        print("📊 Extrayendo conversaciones de SQLite...")
        sqlite_conversations = self._extract_from_sqlite(since, limit)
        conversations.extend(sqlite_conversations)

        # 3. JSON Files
        print("📊 Extrayendo conversaciones de archivos JSON...")
        json_conversations = self._extract_from_json_files()
        conversations.extend(json_conversations)

        # 4. CSV Files
        print("📊 Extrayendo conversaciones de archivos CSV...")
        csv_conversations = self._extract_from_csv_files()
        conversations.extend(csv_conversations)

        print(f"✅ Total conversaciones extraídas: {len(conversations)}")
        return conversations

    def _extract_from_sqlite(
        self,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[ConversationRecord]:
        """Extraer conversaciones de SQLite"""
        conversations: List[ConversationRecord] = []

        if not Path(self.db_path).exists():
            return conversations

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT * FROM ingestion_table"
            if since:
                query += f" WHERE timestamp >= '{since.isoformat()}'"
            query += f" LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()

            # Obtener nombres de columnas
            columns = [description[0] for description in cursor.description]

            for row in rows:
                record = dict(zip(columns, row))
                conv = ConversationRecord(
                    id=record.get("id", ""),
                    source="sqlite",
                    platform=record.get("platform", "unknown"),
                    timestamp=record.get("timestamp", ""),
                    user_query=record.get("user_query", ""),
                    chatbot_response=record.get("chatbot_response"),
                    metadata=json.loads(record.get("metadata", "{}")) if record.get("metadata") else {}
                )
                conversations.append(conv)

            conn.close()
        except Exception as e:
            print(f"Error extrayendo de SQLite: {e}")

        return conversations

    def _extract_from_json_files(self) -> List[ConversationRecord]:
        """Extraer conversaciones de archivos JSON"""
        conversations = []

        # Buscar archivos JSON en training_data
        json_files = list(self.training_data_path.rglob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Intentar diferentes formatos
                if isinstance(data, list):
                    for item in data:
                        conv = self._parse_json_conversation(item, str(json_file))
                        if conv:
                            conversations.append(conv)
                elif isinstance(data, dict):
                    # Bundle format
                    if "conversations" in data:
                        for conv_data in data["conversations"]:
                            conv = self._parse_bundle_conversation(conv_data, str(json_file))
                            if conv:
                                conversations.append(conv)
            except Exception as e:
                print(f"Error leyendo {json_file}: {e}")

        return conversations

    def _extract_from_csv_files(self) -> List[ConversationRecord]:
        """Extraer conversaciones de archivos CSV"""
        conversations = []

        csv_files = list(self.training_data_path.rglob("*.csv"))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        conv = self._parse_csv_row(row, str(csv_file))
                        if conv:
                            conversations.append(conv)
            except Exception as e:
                print(f"Error leyendo {csv_file}: {e}")

        return conversations

    def _parse_json_conversation(self, item: Dict, source_file: str) -> Optional[ConversationRecord]:
        """Parsear conversación desde JSON"""
        try:
            return ConversationRecord(
                id=item.get("id", ""),
                source="json",
                platform=item.get("platform", "unknown"),
                timestamp=item.get("timestamp", ""),
                user_query=item.get("user_query") or item.get("query") or item.get("message", ""),
                chatbot_response=item.get("chatbot_response") or item.get("response") or item.get("reply"),
                metadata={"source_file": source_file, **item.get("metadata", {})}
            )
        except Exception:
            return None

    def _parse_bundle_conversation(self, conv_data: Dict, source_file: str) -> Optional[ConversationRecord]:
        """Parsear conversación desde bundle format"""
        try:
            messages = conv_data.get("messages", [])
            user_query = ""
            chatbot_response = ""
            
            for msg in messages:
                if msg.get("role") == "user":
                    user_query = msg.get("content", "")
                elif msg.get("role") == "assistant":
                    chatbot_response = msg.get("content", "")

            return ConversationRecord(
                id=conv_data.get("id", ""),
                source="json",
                platform=conv_data.get("metadata", {}).get("platform", "unknown"),
                timestamp=conv_data.get("timestamp", ""),
                user_query=user_query,
                chatbot_response=chatbot_response,
                metadata={"source_file": source_file, **conv_data.get("metadata", {})}
            )
        except Exception:
            return None

    def _parse_csv_row(self, row: Dict, source_file: str) -> Optional[ConversationRecord]:
        """Parsear conversación desde CSV"""
        try:
            return ConversationRecord(
                id=row.get("id", ""),
                source="csv",
                platform=row.get("platform", "unknown"),
                timestamp=row.get("timestamp", ""),
                user_query=row.get("user_query") or row.get("query", ""),
                chatbot_response=row.get("chatbot_response") or row.get("response"),
                metadata={"source_file": source_file}
            )
        except Exception:
            return None

    def _create_conversation_record(self, normalized: Dict, source: str) -> ConversationRecord:
        """Crear ConversationRecord desde documento normalizado"""
        return ConversationRecord(
            id=normalized.get("id", ""),
            source=source,
            platform=normalized.get("platform", "unknown"),
            timestamp=normalized.get("timestamp", ""),
            user_query=normalized.get("user_query", ""),
            chatbot_response=normalized.get("chatbot_response"),
            metadata=normalized.get("metadata", {})
        )

    def validate_conversations(
        self,
        conversations: List[ConversationRecord]
    ) -> List[ConversationRecord]:
        """
        Validar conversaciones usando métricas de evaluación

        Args:
            conversations: Lista de conversaciones a validar

        Returns:
            Lista de conversaciones con scores de calidad
        """
        if not self.evaluator:
            print("⚠️  KnowledgeBaseEvaluator no disponible, saltando validación")
            return conversations

        print(f"🔍 Validando {len(conversations)} conversaciones...")

        validated = []
        for i, conv in enumerate(conversations):
            if (i + 1) % 10 == 0:
                print(f"  Procesando {i + 1}/{len(conversations)}...")

            if not conv.chatbot_response:
                continue

            try:
                # Evaluar conversación
                evaluation = self.evaluator.evaluate_interaction(
                    query=conv.user_query,
                    response=conv.chatbot_response,
                    sources_consulted=conv.sources_consulted or []
                )

                # Guardar scores
                conv.quality_scores = {
                    "relevance": evaluation.relevance_score,
                    "groundedness": evaluation.groundedness_score,
                    "coherence": evaluation.coherence_score,
                    "accuracy": evaluation.accuracy_score if hasattr(evaluation, 'accuracy_score') else None,
                    "source_validation": evaluation.source_validation if hasattr(evaluation, 'source_validation') else {}
                }

                validated.append(conv)

            except Exception as e:
                print(f"Error validando conversación {conv.id}: {e}")

        print(f"✅ Validación completada: {len(validated)} conversaciones validadas")
        return validated

    def extract_knowledge(
        self,
        conversations: List[ConversationRecord]
    ) -> List[KnowledgeItem]:
        """
        Extraer conocimiento validado de conversaciones

        Args:
            conversations: Lista de conversaciones validadas

        Returns:
            Lista de items de conocimiento extraídos
        """
        print(f"📚 Extrayendo conocimiento de {len(conversations)} conversaciones...")

        knowledge_items = []

        for conv in conversations:
            # Solo procesar si pasa umbrales de calidad
            if not self._meets_quality_thresholds(conv):
                continue

            # Extraer diferentes tipos de conocimiento
            items = self._extract_from_conversation(conv)
            knowledge_items.extend(items)

        print(f"✅ Extraídos {len(knowledge_items)} items de conocimiento")
        return knowledge_items

    def _meets_quality_thresholds(self, conv: ConversationRecord) -> bool:
        """Verificar si conversación cumple umbrales de calidad"""
        scores = conv.quality_scores
        
        relevance = scores.get("relevance", 0)
        groundedness = scores.get("groundedness", 0)
        coherence = scores.get("coherence", 0)

        return (
            relevance >= self.min_relevance and
            groundedness >= self.min_groundedness and
            coherence >= self.min_coherence
        )

    def _extract_from_conversation(self, conv: ConversationRecord) -> List[KnowledgeItem]:
        """Extraer conocimiento de una conversación específica"""
        items = []

        # Detectar tipos de conocimiento (simplificado - se puede mejorar con NLP)
        query_lower = conv.user_query.lower()
        response_lower = conv.chatbot_response.lower() if conv.chatbot_response else ""

        # Detectar correcciones
        if any(word in response_lower for word in ["corrección", "corregir", "error", "incorrecto"]):
            items.append(KnowledgeItem(
                type="correction",
                content={"query": conv.user_query, "response": conv.chatbot_response},
                confidence=conv.quality_scores.get("relevance", 0.8),
                source_conversation=conv.id,
                validation_status="pending"
            ))

        # Detectar preguntas frecuentes
        if "?" in conv.user_query and conv.quality_scores.get("relevance", 0) > 0.9:
            items.append(KnowledgeItem(
                type="faq",
                content={"question": conv.user_query, "answer": conv.chatbot_response},
                confidence=conv.quality_scores.get("relevance", 0.8),
                source_conversation=conv.id,
                validation_status="pending"
            ))

        # Detectar precios (simplificado)
        if any(word in query_lower for word in ["precio", "cuesta", "costo", "$"]):
            price_info = self._extract_price_info(conv)
            if price_info:
                items.append(KnowledgeItem(
                    type="price",
                    content=price_info,
                    confidence=conv.quality_scores.get("groundedness", 0.8),
                    source_conversation=conv.id,
                    validation_status="pending"
                ))

        return items

    def _extract_price_info(self, conv: ConversationRecord) -> Optional[Dict]:
        """Extraer información de precio de conversación"""
        # Implementación simplificada - se puede mejorar con NLP/Regex
        import re
        
        # Buscar patrones de precio
        price_pattern = r'\$?\s*(\d+[.,]\d+)'
        prices = re.findall(price_pattern, conv.chatbot_response or "")
        
        if prices:
            return {
                "price": float(prices[0].replace(",", ".")),
                "context": conv.user_query,
                "response": conv.chatbot_response
            }
        return None

    def integrate_knowledge(
        self,
        knowledge_items: List[KnowledgeItem]
    ) -> IntegrationReport:
        """
        Integrar conocimiento en Knowledge Base

        Args:
            knowledge_items: Lista de items de conocimiento a integrar

        Returns:
            Reporte de integración
        """
        print(f"🔧 Integrando {len(knowledge_items)} items de conocimiento...")

        report = IntegrationReport(
            timestamp=datetime.now().isoformat(),
            conversations_reviewed=0,
            knowledge_extracted={},
            integration_results={
                "level_1_updates": 0,
                "level_3_updates": 0,
                "faq_additions": 0,
                "rejected": 0
            },
            quality_scores={},
            conflicts_detected=0,
            recommendations=[],
            changes=[]
        )

        # Contar conocimiento extraído por tipo
        for item in knowledge_items:
            report.knowledge_extracted[item.type] = report.knowledge_extracted.get(item.type, 0) + 1

        # Integrar cada item
        for item in knowledge_items:
            if item.confidence < self.min_confidence:
                report.integration_results["rejected"] += 1
                continue

            # Validar contra KB existente
            conflicts = self._check_conflicts(item)
            if conflicts:
                report.conflicts_detected += len(conflicts)
                item.conflicts = conflicts
                item.validation_status = "pending"
                report.recommendations.append(f"Conflicto detectado en {item.type}: {conflicts[0]}")
                continue

            # Integrar según tipo
            if item.type == "price":
                result = self._integrate_price(item)
                if result:
                    report.integration_results["level_1_updates"] += 1
                    report.changes.append(result)
            elif item.type == "faq":
                result = self._integrate_faq(item)
                if result:
                    report.integration_results["faq_additions"] += 1
                    report.changes.append(result)

        return report

    def _check_conflicts(self, item: KnowledgeItem) -> List[str]:
        """Verificar conflictos con KB existente"""
        conflicts: List[str] = []

        # Cargar KB Nivel 1
        kb_file = self.kb_path / self.kb_hierarchy["level_1"][0]
        if not kb_file.exists():
            return conflicts

        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)

            # Verificar conflictos según tipo
            if item.type == "price":
                # Buscar producto en KB y comparar precio
                product_name = item.content.get("product", "")
                new_price = item.content.get("price")
                
                # Simplificado - buscar en estructura de KB
                if "productos" in kb_data:
                    for product in kb_data["productos"]:
                        if product_name.lower() in product.get("nombre", "").lower():
                            existing_price = product.get("precio_shopify")
                            if existing_price and abs(existing_price - new_price) > 0.1:
                                conflicts.append(f"Precio diferente: KB={existing_price}, Nuevo={new_price}")

        except Exception as e:
            print(f"Error verificando conflictos: {e}")

        return conflicts

    def _integrate_price(self, item: KnowledgeItem) -> Optional[Dict]:
        """Integrar precio en KB Nivel 1"""
        # Implementación simplificada - requiere validación manual en producción
        return {
            "type": "price_update",
            "product": item.content.get("product", "unknown"),
            "new_value": item.content.get("price"),
            "source": item.source_conversation,
            "confidence": item.confidence,
            "note": "Requiere validación manual antes de aplicar"
        }

    def _integrate_faq(self, item: KnowledgeItem) -> Optional[Dict]:
        """Integrar FAQ en KB"""
        return {
            "type": "faq_addition",
            "question": item.content.get("question", ""),
            "answer": item.content.get("answer", ""),
            "source": item.source_conversation,
            "confidence": item.confidence
        }

    def generate_report(
        self,
        conversations: List[ConversationRecord],
        knowledge_items: List[KnowledgeItem],  # noqa: ARG002
        integration_report: IntegrationReport
    ) -> Dict:
        """
        Generar reporte completo de integración

        Args:
            conversations: Conversaciones revisadas
            knowledge_items: Items de conocimiento extraídos
            integration_report: Reporte de integración

        Returns:
            Reporte completo en formato JSON
        """
        # Calcular métricas de calidad
        quality_scores = {
            "average_relevance": 0.0,
            "average_groundedness": 0.0,
            "average_coherence": 0.0
        }

        if conversations:
            relevance_scores = [c.quality_scores.get("relevance", 0) for c in conversations if c.quality_scores]
            groundedness_scores = [c.quality_scores.get("groundedness", 0) for c in conversations if c.quality_scores]
            coherence_scores = [c.quality_scores.get("coherence", 0) for c in conversations if c.quality_scores]

            if relevance_scores:
                quality_scores["average_relevance"] = sum(relevance_scores) / len(relevance_scores)
            if groundedness_scores:
                quality_scores["average_groundedness"] = sum(groundedness_scores) / len(groundedness_scores)
            if coherence_scores:
                quality_scores["average_coherence"] = sum(coherence_scores) / len(coherence_scores)

        integration_report.quality_scores = quality_scores
        integration_report.conversations_reviewed = len(conversations)

        # Convertir a dict
        report_dict = asdict(integration_report)

        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_path / f"integration_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"✅ Reporte guardado en: {report_file}")

        return report_dict

    def run_full_integration(
        self,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> Dict:
        """
        Ejecutar proceso completo de integración

        Args:
            since: Fecha desde la cual revisar
            limit: Límite de conversaciones

        Returns:
            Reporte completo
        """
        print("🚀 Iniciando proceso completo de integración de conocimiento...\n")

        # Fase 1: Revisar conversaciones
        conversations = self.review_conversations(since=since, limit=limit)

        # Fase 2: Validar conversaciones
        validated_conversations = self.validate_conversations(conversations)

        # Fase 3: Extraer conocimiento
        knowledge_items = self.extract_knowledge(validated_conversations)

        # Fase 4: Integrar conocimiento
        integration_report = self.integrate_knowledge(knowledge_items)

        # Fase 5: Generar reporte
        report = self.generate_report(validated_conversations, knowledge_items, integration_report)

        print("\n✅ Proceso de integración completado!")
        print(f"   - Conversaciones revisadas: {report['conversations_reviewed']}")
        print(f"   - Conocimiento extraído: {sum(report['knowledge_extracted'].values())}")
        print(f"   - Cambios realizados: {sum(report['integration_results'].values())}")
        print(f"   - Conflictos detectados: {report['conflicts_detected']}")

        return report


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Agente Integrador de Conocimiento")
    parser.add_argument("--since", type=str, help="Fecha desde (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=1000, help="Límite de conversaciones")
    parser.add_argument("--kb-path", type=str, default="./gpt_configs", help="Ruta a KB")
    parser.add_argument("--output", type=str, default="./integration_output", help="Ruta de salida")

    args = parser.parse_args()

    # Parsear fecha
    since = None
    if args.since:
        try:
            since = datetime.fromisoformat(args.since)
        except ValueError:
            print(f"Error: Fecha inválida: {args.since}")
            return

    # Crear agente
    agente = AgenteIntegradorConocimiento(
        kb_path=args.kb_path,
        output_path=args.output
    )

    # Ejecutar integración
    report = agente.run_full_integration(since=since, limit=args.limit)

    print("\n📊 Resumen:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
