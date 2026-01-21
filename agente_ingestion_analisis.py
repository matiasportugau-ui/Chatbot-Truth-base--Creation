#!/usr/bin/env python3
"""
Agente de Ingestion y Análisis Completo
========================================

Agente que:
1. Genera tabla de ingestion para el sistema de chatbot
2. Analiza todos los inputs de cotizaciones
3. Analiza consultas de MercadoLibre, Instagram y Facebook
4. Analiza y revisa respuestas del chatbot contra usuarios
5. Genera reportes de análisis completos
"""

import json
import csv
import re
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
import sys

# Importar componentes existentes
sys.path.insert(0, str(Path(__file__).parent))
try:
    from motor_cotizacion_panelin import MotorCotizacionPanelin
except ImportError:
    MotorCotizacionPanelin = None

try:
    from gpt_simulation_agent.agent_system.agent_social_ingestion import (
        SocialIngestionEngine,
    )
    from gpt_simulation_agent.agent_system.utils.facebook_api import FacebookAPIClient
    from gpt_simulation_agent.agent_system.utils.instagram_api import InstagramAPIClient
    from gpt_simulation_agent.agent_system.utils.mercadolibre_api import (
        MercadoLibreAPIClient,
    )
    from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient
except ImportError:
    SocialIngestionEngine = None
    FacebookAPIClient = None
    InstagramAPIClient = None
    MercadoLibreAPIClient = None
    MongoDBClient = None


@dataclass
class IngestionRecord:
    """Registro de ingestion unificado"""

    id: str
    source: str  # 'quote', 'mercadolibre', 'instagram', 'facebook', 'chatbot'
    platform: str
    timestamp: str
    user_query: str
    chatbot_response: Optional[str] = None
    metadata: Dict = None
    analysis: Dict = None

    def to_dict(self):
        return asdict(self)


class AgenteIngestionAnalisis:
    """Agente principal de ingestion y análisis"""

    def __init__(self, db_path: str = "ingestion_database.db"):
        """
        Inicializar agente

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.motor = MotorCotizacionPanelin() if MotorCotizacionPanelin else None
        self.social_engine = SocialIngestionEngine() if SocialIngestionEngine else None
        self.ml_client = MercadoLibreAPIClient() if MercadoLibreAPIClient else None
        self.mongodb_client = MongoDBClient() if MongoDBClient else None

        # Rutas de datos
        self.csv_inputs = "/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv"
        self.training_data_dir = Path("training_data")
        self.output_dir = Path("ingestion_analysis_output")
        self.output_dir.mkdir(exist_ok=True)

        # Inicializar base de datos
        self._init_database()

    def _init_database(self):
        """Inicializar base de datos SQLite para ingestion table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de ingestion
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestion_table (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                platform TEXT,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                chatbot_response TEXT,
                metadata TEXT,
                analysis TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Tabla de análisis de cotizaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quote_analysis (
                id TEXT PRIMARY KEY,
                ingestion_id TEXT,
                product_code TEXT,
                product_name TEXT,
                price REAL,
                quantity INTEGER,
                total REAL,
                timestamp TEXT,
                analysis_result TEXT,
                FOREIGN KEY (ingestion_id) REFERENCES ingestion_table(id)
            )
        """
        )

        # Tabla de análisis de redes sociales
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS social_media_analysis (
                id TEXT PRIMARY KEY,
                ingestion_id TEXT,
                platform TEXT,
                interaction_type TEXT,
                content TEXT,
                engagement_score REAL,
                sentiment TEXT,
                topics TEXT,
                requires_response BOOLEAN,
                timestamp TEXT,
                FOREIGN KEY (ingestion_id) REFERENCES ingestion_table(id)
            )
        """
        )

        # Tabla de análisis de respuestas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS response_analysis (
                id TEXT PRIMARY KEY,
                ingestion_id TEXT,
                relevance_score REAL,
                accuracy_score REAL,
                completeness_score REAL,
                sentiment_match BOOLEAN,
                issues_detected TEXT,
                recommendations TEXT,
                timestamp TEXT,
                FOREIGN KEY (ingestion_id) REFERENCES ingestion_table(id)
            )
        """
        )

        # Índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_source ON ingestion_table(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_platform ON ingestion_table(platform)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON ingestion_table(timestamp)"
        )

        conn.commit()
        conn.close()

    def generar_tabla_ingestion(self) -> Dict:
        """
        Genera tabla de ingestion completa desde todas las fuentes

        Returns:
            Dict con resumen de ingestion
        """
        print("=" * 70)
        print("📊 GENERANDO TABLA DE INGESTION")
        print("=" * 70)

        records = []

        # 1. Ingestion de cotizaciones
        print("\n1️⃣  Ingestionando cotizaciones...")
        quote_records = self._ingest_quotes()
        records.extend(quote_records)
        print(f"   ✅ {len(quote_records)} cotizaciones procesadas")

        # 2. Ingestion de MercadoLibre
        print("\n2️⃣  Ingestionando consultas de MercadoLibre...")
        ml_records = self._ingest_mercadolibre()
        records.extend(ml_records)
        print(f"   ✅ {len(ml_records)} consultas de MercadoLibre procesadas")

        # 3. Ingestion de Instagram
        print("\n3️⃣  Ingestionando consultas de Instagram...")
        ig_records = self._ingest_instagram()
        records.extend(ig_records)
        print(f"   ✅ {len(ig_records)} consultas de Instagram procesadas")

        # 4. Ingestion de Facebook
        print("\n4️⃣  Ingestionando consultas de Facebook...")
        fb_records = self._ingest_facebook()
        records.extend(fb_records)
        print(f"   ✅ {len(fb_records)} consultas de Facebook procesadas")

        # 5. Ingestion de MongoDB
        print("\n5️⃣  Ingestionando datos de MongoDB...")
        mongodb_records = self._ingest_mongodb()
        records.extend(mongodb_records)
        print(f"   ✅ {len(mongodb_records)} registros de MongoDB procesados")

        # 6. Guardar en base de datos
        print("\n6️⃣  Guardando en base de datos...")
        saved_count = self._save_to_database(records)
        print(f"   ✅ {saved_count} registros guardados")

        # 7. Generar resumen
        resumen = self._generar_resumen_ingestion(records)

        return {
            "total_records": len(records),
            "by_source": resumen["by_source"],
            "by_platform": resumen["by_platform"],
            "date_range": resumen["date_range"],
            "database_path": self.db_path,
        }

    def _ingest_quotes(self) -> List[IngestionRecord]:
        """Ingestiona inputs de cotizaciones desde CSV"""
        records = []

        if not os.path.exists(self.csv_inputs):
            print(f"   ⚠️  CSV no encontrado: {self.csv_inputs}")
            return records

        try:
            with open(self.csv_inputs, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                rows = list(reader)

                if len(rows) < 3:
                    return records

                headers = [h.strip() for h in rows[1]]
                header_map = {h: i for i, h in enumerate(headers)}

                for idx, row in enumerate(rows[2:], start=3):
                    if len(row) < len(headers):
                        row.extend([""] * (len(headers) - len(row)))

                    def get_value(key, default=""):
                        col_idx = header_map.get(key, -1)
                        return (
                            row[col_idx].strip()
                            if col_idx >= 0 and col_idx < len(row)
                            else default
                        )

                    consulta = get_value("Consulta", "")
                    if not consulta:
                        continue

                    record = IngestionRecord(
                        id=f"quote_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        source="quote",
                        platform="csv",
                        timestamp=get_value("Fecha", datetime.now().isoformat()),
                        user_query=consulta,
                        chatbot_response=None,
                        metadata={
                            "cliente": get_value("Cliente"),
                            "producto": get_value("Producto"),
                            "dimensiones": get_value("Dimensiones"),
                            "luz": get_value("Luz"),
                            "fijacion": get_value("Fijación"),
                            "notas": get_value("Notas"),
                            "fila": idx,
                        },
                        analysis=None,
                    )

                    records.append(record)

        except Exception as e:
            print(f"   ⚠️  Error leyendo CSV: {e}")

        return records

    def _ingest_mercadolibre(self) -> List[IngestionRecord]:
        """Ingestiona consultas de MercadoLibre"""
        records = []

        # Intentar ingestion desde API si está disponible
        if self.ml_client:
            try:
                questions = self.ml_client.get_questions(limit=100)
                messages = self.ml_client.get_messages(limit=100)

                for question in questions:
                    normalized = self.ml_client.normalize_interaction(
                        question, "question"
                    )
                    record = IngestionRecord(
                        id=f"ml_{normalized['id']}",
                        source="mercadolibre",
                        platform="mercadolibre",
                        timestamp=normalized["timestamp"],
                        user_query=normalized["content"],
                        chatbot_response=None,
                        metadata={
                            "type": normalized["type"],
                            "context": normalized["context"],
                            "engagement": normalized["engagement"],
                            "source": "api",
                        },
                        analysis=None,
                    )
                    records.append(record)

                for message in messages:
                    normalized = self.ml_client.normalize_interaction(
                        message, "message"
                    )
                    record = IngestionRecord(
                        id=f"ml_{normalized['id']}",
                        source="mercadolibre",
                        platform="mercadolibre",
                        timestamp=normalized["timestamp"],
                        user_query=normalized["content"],
                        chatbot_response=None,
                        metadata={
                            "type": normalized["type"],
                            "context": normalized["context"],
                            "source": "api",
                        },
                        analysis=None,
                    )
                    records.append(record)
            except Exception as e:
                print(f"   ⚠️  Error en ingestion desde API de MercadoLibre: {e}")

        # Buscar archivos de MercadoLibre en training_data
        ml_dir = self.training_data_dir / "mercadolibre"
        if not ml_dir.exists():
            ml_dir.mkdir(parents=True, exist_ok=True)
            if not records:
                print(f"   ⚠️  Directorio de MercadoLibre creado: {ml_dir}")
                print(f"   💡 Coloca archivos JSON de consultas de MercadoLibre aquí")
            return records

        # Buscar archivos JSON
        ml_files = list(ml_dir.glob("*.json"))

        for ml_file in ml_files:
            try:
                with open(ml_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    if isinstance(data, list):
                        for item in data:
                            record = IngestionRecord(
                                id=f"ml_{item.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                                source="mercadolibre",
                                platform="mercadolibre",
                                timestamp=item.get(
                                    "timestamp", datetime.now().isoformat()
                                ),
                                user_query=item.get(
                                    "question",
                                    item.get("consulta", item.get("message", "")),
                                ),
                                chatbot_response=item.get("response", None),
                                metadata={
                                    "product_id": item.get("product_id"),
                                    "user_id": item.get("user_id"),
                                    "listing_url": item.get("listing_url"),
                                    "category": item.get("category"),
                                    "file_source": str(ml_file),
                                },
                                analysis=None,
                            )
                            records.append(record)
                    elif isinstance(data, dict):
                        record = IngestionRecord(
                            id=f"ml_{data.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                            source="mercadolibre",
                            platform="mercadolibre",
                            timestamp=data.get("timestamp", datetime.now().isoformat()),
                            user_query=data.get(
                                "question",
                                data.get("consulta", data.get("message", "")),
                            ),
                            chatbot_response=data.get("response", None),
                            metadata={
                                "product_id": data.get("product_id"),
                                "user_id": data.get("user_id"),
                                "listing_url": data.get("listing_url"),
                                "category": data.get("category"),
                                "file_source": str(ml_file),
                            },
                            analysis=None,
                        )
                        records.append(record)

            except Exception as e:
                print(f"   ⚠️  Error leyendo {ml_file}: {e}")

        return records

    def _ingest_instagram(self) -> List[IngestionRecord]:
        """Ingestiona consultas de Instagram"""
        records = []

        # Usar SocialIngestionEngine si está disponible
        if self.social_engine:
            try:
                results = self.social_engine.ingest(
                    platforms=["instagram"], days_back=90, limit_per_platform=1000
                )

                # Leer archivos generados
                ig_dir = self.training_data_dir / "social_media" / "instagram"
                if ig_dir.exists():
                    for json_file in ig_dir.rglob("*.json"):
                        try:
                            with open(json_file, "r", encoding="utf-8") as f:
                                interactions = json.load(f)

                                for interaction in interactions:
                                    record = IngestionRecord(
                                        id=f"ig_{interaction.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                                        source="instagram",
                                        platform="instagram",
                                        timestamp=interaction.get(
                                            "timestamp", datetime.now().isoformat()
                                        ),
                                        user_query=interaction.get("content", ""),
                                        chatbot_response=None,
                                        metadata={
                                            "type": interaction.get("type"),
                                            "user": interaction.get("user", {}),
                                            "engagement": interaction.get(
                                                "engagement", {}
                                            ),
                                            "context": interaction.get("context", {}),
                                            "file_source": str(json_file),
                                        },
                                        analysis=None,
                                    )
                                    records.append(record)
                        except Exception as e:
                            print(f"   ⚠️  Error leyendo {json_file}: {e}")
            except Exception as e:
                print(f"   ⚠️  Error en ingestion de Instagram: {e}")

        # También buscar en training_data directamente
        ig_dir = self.training_data_dir / "social_media" / "instagram"
        if ig_dir.exists():
            for json_file in ig_dir.glob("*.json"):
                if json_file.name.startswith("sample_"):
                    continue  # Skip samples

                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        interactions = json.load(f)

                        if isinstance(interactions, list):
                            for interaction in interactions:
                                record = IngestionRecord(
                                    id=f"ig_{interaction.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                                    source="instagram",
                                    platform="instagram",
                                    timestamp=interaction.get(
                                        "timestamp", datetime.now().isoformat()
                                    ),
                                    user_query=interaction.get(
                                        "content", interaction.get("text", "")
                                    ),
                                    chatbot_response=None,
                                    metadata={
                                        "type": interaction.get("type"),
                                        "user": interaction.get("user", {}),
                                        "engagement": interaction.get("engagement", {}),
                                        "file_source": str(json_file),
                                    },
                                    analysis=None,
                                )
                                records.append(record)
                except Exception as e:
                    print(f"   ⚠️  Error leyendo {json_file}: {e}")

        return records

    def _ingest_facebook(self) -> List[IngestionRecord]:
        """Ingestiona consultas de Facebook"""
        records = []

        # Usar SocialIngestionEngine si está disponible
        if self.social_engine:
            try:
                results = self.social_engine.ingest(
                    platforms=["facebook"], days_back=90, limit_per_platform=1000
                )

                # Leer archivos generados
                fb_dir = self.training_data_dir / "social_media" / "facebook"
                if fb_dir.exists():
                    for json_file in fb_dir.rglob("*.json"):
                        try:
                            with open(json_file, "r", encoding="utf-8") as f:
                                interactions = json.load(f)

                                for interaction in interactions:
                                    record = IngestionRecord(
                                        id=f"fb_{interaction.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                                        source="facebook",
                                        platform="facebook",
                                        timestamp=interaction.get(
                                            "timestamp", datetime.now().isoformat()
                                        ),
                                        user_query=interaction.get("content", ""),
                                        chatbot_response=None,
                                        metadata={
                                            "type": interaction.get("type"),
                                            "user": interaction.get("user", {}),
                                            "engagement": interaction.get(
                                                "engagement", {}
                                            ),
                                            "context": interaction.get("context", {}),
                                            "file_source": str(json_file),
                                        },
                                        analysis=None,
                                    )
                                    records.append(record)
                        except Exception as e:
                            print(f"   ⚠️  Error leyendo {json_file}: {e}")
            except Exception as e:
                print(f"   ⚠️  Error en ingestion de Facebook: {e}")

        # También buscar en training_data directamente
        fb_dir = self.training_data_dir / "social_media" / "facebook"
        if fb_dir.exists():
            for json_file in fb_dir.glob("*.json"):
                if json_file.name.startswith("sample_"):
                    continue  # Skip samples

                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        interactions = json.load(f)

                        if isinstance(interactions, list):
                            for interaction in interactions:
                                record = IngestionRecord(
                                    id=f"fb_{interaction.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}",
                                    source="facebook",
                                    platform="facebook",
                                    timestamp=interaction.get(
                                        "timestamp", datetime.now().isoformat()
                                    ),
                                    user_query=interaction.get(
                                        "content", interaction.get("message", "")
                                    ),
                                    chatbot_response=None,
                                    metadata={
                                        "type": interaction.get("type"),
                                        "user": interaction.get("user", {}),
                                        "engagement": interaction.get("engagement", {}),
                                        "file_source": str(json_file),
                                    },
                                    analysis=None,
                                )
                                records.append(record)
                except Exception as e:
                    print(f"   ⚠️  Error leyendo {json_file}: {e}")

        return records

    def _ingest_mongodb(self) -> List[IngestionRecord]:
        """Ingestiona datos de MongoDB"""
        records = []

        if not self.mongodb_client or not self.mongodb_client.db:
            print(
                f"   ⚠️  MongoDB no conectado. Configurar MONGODB_CONNECTION_STRING y MONGODB_DATABASE_NAME"
            )
            return records

        try:
            # 1. Extraer cotizaciones
            quotes = self.mongodb_client.extract_quotes(limit=1000)
            for quote in quotes:
                normalized = self.mongodb_client.normalize_document(quote, "quote")
                record = IngestionRecord(
                    id=f"mongo_quote_{normalized['id']}",
                    source="quote",
                    platform="mongodb",
                    timestamp=normalized["timestamp"],
                    user_query=normalized["user_query"],
                    chatbot_response=normalized.get("chatbot_response"),
                    metadata={
                        "source": "mongodb",
                        "collection": normalized["metadata"].get(
                            "collection", "quotes"
                        ),
                        "original_doc_id": normalized["id"],
                    },
                    analysis=None,
                )
                records.append(record)

            # 2. Extraer conversaciones
            conversations = self.mongodb_client.extract_conversations(limit=1000)
            for conv in conversations:
                normalized = self.mongodb_client.normalize_document(
                    conv, "conversation"
                )
                record = IngestionRecord(
                    id=f"mongo_conv_{normalized['id']}",
                    source="chatbot",
                    platform="mongodb",
                    timestamp=normalized["timestamp"],
                    user_query=normalized["user_query"],
                    chatbot_response=normalized.get("chatbot_response"),
                    metadata={
                        "source": "mongodb",
                        "collection": normalized["metadata"].get(
                            "collection", "conversations"
                        ),
                        "original_doc_id": normalized["id"],
                    },
                    analysis=None,
                )
                records.append(record)

            # 3. Extraer redes sociales
            for platform in ["facebook", "instagram", "mercadolibre"]:
                social_data = self.mongodb_client.extract_social_media(
                    platform=platform, limit=500
                )
                for social in social_data:
                    normalized = self.mongodb_client.normalize_document(
                        social, "social_media"
                    )
                    record = IngestionRecord(
                        id=f"mongo_{platform}_{normalized['id']}",
                        source=platform,
                        platform="mongodb",
                        timestamp=normalized["timestamp"],
                        user_query=normalized["user_query"],
                        chatbot_response=normalized.get("chatbot_response"),
                        metadata={
                            "source": "mongodb",
                            "collection": normalized["metadata"].get(
                                "collection", f"{platform}_interactions"
                            ),
                            "original_doc_id": normalized["id"],
                            "platform": platform,
                        },
                        analysis=None,
                    )
                    records.append(record)

        except Exception as e:
            print(f"   ⚠️  Error en ingestion de MongoDB: {e}")
            import traceback

            traceback.print_exc()

        return records

    def _save_to_database(self, records: List[IngestionRecord]) -> int:
        """Guarda registros en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved = 0
        for record in records:
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO ingestion_table 
                    (id, source, platform, timestamp, user_query, chatbot_response, metadata, analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        record.id,
                        record.source,
                        record.platform,
                        record.timestamp,
                        record.user_query,
                        record.chatbot_response,
                        json.dumps(record.metadata) if record.metadata else None,
                        json.dumps(record.analysis) if record.analysis else None,
                    ),
                )
                saved += 1
            except Exception as e:
                print(f"   ⚠️  Error guardando registro {record.id}: {e}")

        conn.commit()
        conn.close()

        return saved

    def _generar_resumen_ingestion(self, records: List[IngestionRecord]) -> Dict:
        """Genera resumen de ingestion"""
        by_source = defaultdict(int)
        by_platform = defaultdict(int)
        timestamps = []

        for record in records:
            by_source[record.source] += 1
            by_platform[record.platform] += 1
            if record.timestamp:
                try:
                    timestamps.append(
                        datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))
                    )
                except:
                    pass

        date_range = {}
        if timestamps:
            date_range["min"] = min(timestamps).isoformat()
            date_range["max"] = max(timestamps).isoformat()

        return {
            "by_source": dict(by_source),
            "by_platform": dict(by_platform),
            "date_range": date_range,
        }

    def analizar_cotizaciones(self) -> Dict:
        """
        Analiza todos los inputs de cotizaciones

        Returns:
            Dict con análisis de cotizaciones
        """
        print("\n" + "=" * 70)
        print("📊 ANALIZANDO COTIZACIONES")
        print("=" * 70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Obtener todas las cotizaciones
        cursor.execute("SELECT * FROM ingestion_table WHERE source = 'quote'")
        quotes = cursor.fetchall()

        analyses = []

        for quote_row in quotes:
            quote_id = quote_row[0]
            user_query = quote_row[4]
            metadata_str = quote_row[6]

            if not metadata_str:
                continue

            try:
                metadata = json.loads(metadata_str)
            except:
                continue

            # Analizar cotización
            analysis = self._analizar_quote_input(user_query, metadata)

            # Guardar análisis
            if self.motor:
                try:
                    # Intentar generar cotización
                    producto = metadata.get("producto", "")
                    dimensiones = metadata.get("dimensiones", "")

                    # Extraer parámetros básicos
                    producto_match = re.search(
                        r"(ISODEC|ISOPANEL|ISOROOF|ISOWALL)", user_query.upper()
                    )
                    espesor_match = re.search(r"(\d+)\s*mm", user_query.upper())

                    if producto_match and espesor_match:
                        analysis["can_generate_quote"] = True
                    else:
                        analysis["can_generate_quote"] = False
                        analysis["missing_params"] = []
                        if not producto_match:
                            analysis["missing_params"].append("producto")
                        if not espesor_match:
                            analysis["missing_params"].append("espesor")
                except Exception as e:
                    analysis["error"] = str(e)

            # Guardar en tabla de análisis
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO quote_analysis
                    (id, ingestion_id, product_code, product_name, price, quantity, total, timestamp, analysis_result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"qa_{quote_id}",
                        quote_id,
                        analysis.get("product_code"),
                        analysis.get("product_name"),
                        analysis.get("price"),
                        analysis.get("quantity"),
                        analysis.get("total"),
                        datetime.now().isoformat(),
                        json.dumps(analysis),
                    ),
                )
            except Exception as e:
                print(f"   ⚠️  Error guardando análisis: {e}")

            analyses.append({"id": quote_id, "query": user_query, "analysis": analysis})

        conn.commit()
        conn.close()

        # Generar resumen
        resumen = self._generar_resumen_cotizaciones(analyses)

        return {"total_quotes": len(analyses), "analyses": analyses, "summary": resumen}

    def _analizar_quote_input(self, query: str, metadata: Dict) -> Dict:
        """Analiza un input de cotización individual"""
        analysis = {
            "query": query,
            "product_detected": False,
            "product_code": None,
            "product_name": None,
            "espesor_detected": False,
            "espesor": None,
            "dimensiones_detected": False,
            "dimensiones": None,
            "luz_detected": False,
            "luz": None,
            "fijacion_detected": False,
            "fijacion": None,
            "completeness_score": 0.0,
            "issues": [],
            "recommendations": [],
        }

        query_upper = query.upper()

        # Detectar producto
        productos = {
            "ISODEC EPS": r"ISODEC.*EPS|EPS.*ISODEC",
            "ISODEC PIR": r"ISODEC.*PIR|PIR.*ISODEC",
            "ISOPANEL EPS": r"ISOPANEL.*EPS|EPS.*ISOPANEL",
            "ISOROOF": r"ISOROOF",
            "ISOWALL PIR": r"ISOWALL.*PIR|PIR.*ISOWALL",
        }

        for producto, pattern in productos.items():
            if re.search(pattern, query_upper):
                analysis["product_detected"] = True
                analysis["product_code"] = producto
                analysis["product_name"] = producto
                break

        # Detectar espesor
        espesor_match = re.search(r"(\d+)\s*mm", query_upper)
        if espesor_match:
            analysis["espesor_detected"] = True
            analysis["espesor"] = espesor_match.group(1)

        # Detectar dimensiones
        dim_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:m|metro|metros)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:m|metro|metros)?",
            query_upper,
        )
        if dim_match:
            analysis["dimensiones_detected"] = True
            analysis["dimensiones"] = {
                "largo": float(dim_match.group(1)),
                "ancho": float(dim_match.group(2)),
            }

        # Detectar luz
        luz_match = re.search(r"LUZ[:\s]*(\d+(?:\.\d+)?)", query_upper)
        if luz_match:
            analysis["luz_detected"] = True
            analysis["luz"] = float(luz_match.group(1))

        # Detectar fijación
        if re.search(r"HORMIG[OÓ]N|CONCRETO", query_upper):
            analysis["fijacion_detected"] = True
            analysis["fijacion"] = "hormigon"
        elif re.search(r"METAL|MET[ÁA]LIC", query_upper):
            analysis["fijacion_detected"] = True
            analysis["fijacion"] = "metal"
        elif re.search(r"MADERA", query_upper):
            analysis["fijacion_detected"] = True
            analysis["fijacion"] = "madera"

        # Calcular completeness score
        required_fields = [
            "product_detected",
            "espesor_detected",
            "dimensiones_detected",
        ]
        optional_fields = ["luz_detected", "fijacion_detected"]

        required_score = sum(1 for field in required_fields if analysis[field]) / len(
            required_fields
        )
        optional_score = sum(1 for field in optional_fields if analysis[field]) / len(
            optional_fields
        )

        analysis["completeness_score"] = (required_score * 0.7) + (optional_score * 0.3)

        # Detectar issues
        if not analysis["product_detected"]:
            analysis["issues"].append("Producto no detectado")
        if not analysis["espesor_detected"]:
            analysis["issues"].append("Espesor no detectado")
        if not analysis["dimensiones_detected"]:
            analysis["issues"].append("Dimensiones no detectadas")

        # Recomendaciones
        if analysis["completeness_score"] < 0.7:
            analysis["recommendations"].append(
                "Input incompleto - requiere más información"
            )

        return analysis

    def _generar_resumen_cotizaciones(self, analyses: List[Dict]) -> Dict:
        """Genera resumen de análisis de cotizaciones"""
        total = len(analyses)
        if total == 0:
            return {}

        completeness_scores = [a["analysis"]["completeness_score"] for a in analyses]
        avg_completeness = sum(completeness_scores) / len(completeness_scores)

        productos = defaultdict(int)
        for a in analyses:
            producto = a["analysis"].get("product_code", "Unknown")
            productos[producto] += 1

        issues_count = sum(len(a["analysis"].get("issues", [])) for a in analyses)

        return {
            "total": total,
            "avg_completeness": avg_completeness,
            "product_distribution": dict(productos),
            "total_issues": issues_count,
            "avg_issues_per_quote": issues_count / total if total > 0 else 0,
        }

    def analizar_redes_sociales(self) -> Dict:
        """
        Analiza consultas de MercadoLibre, Instagram y Facebook

        Returns:
            Dict con análisis de redes sociales
        """
        print("\n" + "=" * 70)
        print("📱 ANALIZANDO REDES SOCIALES")
        print("=" * 70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Obtener todas las consultas de redes sociales
        cursor.execute(
            """
            SELECT * FROM ingestion_table 
            WHERE source IN ('mercadolibre', 'instagram', 'facebook')
        """
        )
        social_records = cursor.fetchall()

        analyses = []

        for record in social_records:
            record_id = record[0]
            source = record[1]
            platform = record[2]
            user_query = record[4]
            metadata_str = record[6]

            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except:
                metadata = {}

            # Analizar consulta
            analysis = self._analizar_social_query(user_query, source, metadata)

            # Guardar análisis
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO social_media_analysis
                    (id, ingestion_id, platform, interaction_type, content, engagement_score, 
                     sentiment, topics, requires_response, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"sm_{record_id}",
                        record_id,
                        platform,
                        metadata.get("type", "unknown"),
                        user_query,
                        analysis.get("engagement_score", 0.0),
                        analysis.get("sentiment", "neutral"),
                        json.dumps(analysis.get("topics", [])),
                        analysis.get("requires_response", False),
                        datetime.now().isoformat(),
                    ),
                )
            except Exception as e:
                print(f"   ⚠️  Error guardando análisis: {e}")

            analyses.append(
                {
                    "id": record_id,
                    "platform": platform,
                    "query": user_query,
                    "analysis": analysis,
                }
            )

        conn.commit()
        conn.close()

        # Generar resumen
        resumen = self._generar_resumen_social(analyses)

        return {
            "total_queries": len(analyses),
            "analyses": analyses,
            "summary": resumen,
        }

    def _analizar_social_query(self, query: str, source: str, metadata: Dict) -> Dict:
        """Analiza una consulta de red social"""
        analysis = {
            "query": query,
            "is_question": False,
            "requires_response": False,
            "sentiment": "neutral",
            "topics": [],
            "engagement_score": 0.0,
            "product_mentioned": False,
            "price_mentioned": False,
            "urgency": "low",
        }

        query_lower = query.lower()

        # Detectar si es pregunta
        question_words = [
            "?",
            "cuanto",
            "cuál",
            "qué",
            "cómo",
            "dónde",
            "cuándo",
            "precio",
            "costo",
        ]
        analysis["is_question"] = (
            any(word in query_lower for word in question_words) or "?" in query
        )

        # Detectar si requiere respuesta
        analysis["requires_response"] = analysis["is_question"] or any(
            word in query_lower
            for word in ["necesito", "quiero", "busco", "consulta", "información"]
        )

        # Análisis de sentimiento básico
        positive_words = ["gracias", "excelente", "bueno", "perfecto", "genial"]
        negative_words = ["mal", "malo", "problema", "error", "no funciona"]

        positive_count = sum(1 for word in positive_words if word in query_lower)
        negative_count = sum(1 for word in negative_words if word in query_lower)

        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"
        else:
            analysis["sentiment"] = "neutral"

        # Detectar productos mencionados
        productos = ["isodec", "isopanel", "isoroof", "isowall", "panel", "aislamiento"]
        analysis["product_mentioned"] = any(
            producto in query_lower for producto in productos
        )

        # Detectar mención de precio
        price_words = ["precio", "costo", "cuanto", "valor", "tarifa", "$", "usd"]
        analysis["price_mentioned"] = any(word in query_lower for word in price_words)

        # Detectar urgencia
        urgency_words = ["urgente", "rápido", "inmediato", "ya", "ahora"]
        if any(word in query_lower for word in urgency_words):
            analysis["urgency"] = "high"
        elif analysis["requires_response"]:
            analysis["urgency"] = "medium"

        # Calcular engagement score
        score = 0.0
        if analysis["is_question"]:
            score += 0.3
        if analysis["requires_response"]:
            score += 0.3
        if analysis["product_mentioned"]:
            score += 0.2
        if analysis["price_mentioned"]:
            score += 0.2

        # Ajustar por engagement de metadata si existe
        if "engagement" in metadata:
            engagement = metadata["engagement"]
            likes = engagement.get("likes", 0)
            replies = engagement.get("replies", 0)
            score += min(0.2, (likes + replies * 2) / 100.0)

        analysis["engagement_score"] = min(1.0, score)

        # Extraer topics
        topics = []
        if analysis["product_mentioned"]:
            topics.append("product_inquiry")
        if analysis["price_mentioned"]:
            topics.append("pricing")
        if "cotizacion" in query_lower or "presupuesto" in query_lower:
            topics.append("quotation")
        if "instalacion" in query_lower or "montaje" in query_lower:
            topics.append("installation")

        analysis["topics"] = topics

        return analysis

    def _generar_resumen_social(self, analyses: List[Dict]) -> Dict:
        """Genera resumen de análisis de redes sociales"""
        total = len(analyses)
        if total == 0:
            return {}

        by_platform = defaultdict(int)
        questions = 0
        requires_response = 0
        sentiment_dist = defaultdict(int)
        avg_engagement = 0.0

        for a in analyses:
            by_platform[a["platform"]] += 1
            if a["analysis"].get("is_question"):
                questions += 1
            if a["analysis"].get("requires_response"):
                requires_response += 1
            sentiment_dist[a["analysis"].get("sentiment", "neutral")] += 1
            avg_engagement += a["analysis"].get("engagement_score", 0.0)

        avg_engagement = avg_engagement / total if total > 0 else 0.0

        return {
            "total": total,
            "by_platform": dict(by_platform),
            "questions": questions,
            "question_rate": questions / total if total > 0 else 0.0,
            "requires_response": requires_response,
            "response_rate": requires_response / total if total > 0 else 0.0,
            "sentiment_distribution": dict(sentiment_dist),
            "avg_engagement_score": avg_engagement,
        }

    def analizar_respuestas(self) -> Dict:
        """
        Analiza y revisa respuestas del chatbot contra usuarios

        Returns:
            Dict con análisis de respuestas
        """
        print("\n" + "=" * 70)
        print("💬 ANALIZANDO RESPUESTAS DEL CHATBOT")
        print("=" * 70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Obtener registros con respuestas del chatbot
        cursor.execute(
            """
            SELECT * FROM ingestion_table 
            WHERE chatbot_response IS NOT NULL AND chatbot_response != ''
        """
        )
        records_with_responses = cursor.fetchall()

        analyses = []

        for record in records_with_responses:
            record_id = record[0]
            user_query = record[4]
            chatbot_response = record[5]

            # Analizar respuesta
            analysis = self._analizar_respuesta(user_query, chatbot_response)

            # Guardar análisis
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO response_analysis
                    (id, ingestion_id, relevance_score, accuracy_score, completeness_score,
                     sentiment_match, issues_detected, recommendations, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"ra_{record_id}",
                        record_id,
                        analysis.get("relevance_score", 0.0),
                        analysis.get("accuracy_score", 0.0),
                        analysis.get("completeness_score", 0.0),
                        analysis.get("sentiment_match", False),
                        json.dumps(analysis.get("issues", [])),
                        json.dumps(analysis.get("recommendations", [])),
                        datetime.now().isoformat(),
                    ),
                )
            except Exception as e:
                print(f"   ⚠️  Error guardando análisis: {e}")

            analyses.append(
                {
                    "id": record_id,
                    "user_query": user_query,
                    "chatbot_response": chatbot_response,
                    "analysis": analysis,
                }
            )

        conn.commit()
        conn.close()

        # Generar resumen
        resumen = self._generar_resumen_respuestas(analyses)

        return {
            "total_responses": len(analyses),
            "analyses": analyses,
            "summary": resumen,
        }

    def _analizar_respuesta(self, user_query: str, chatbot_response: str) -> Dict:
        """Analiza una respuesta del chatbot contra la consulta del usuario"""
        analysis = {
            "relevance_score": 0.0,
            "accuracy_score": 0.0,
            "completeness_score": 0.0,
            "sentiment_match": False,
            "issues": [],
            "recommendations": [],
        }

        query_lower = user_query.lower()
        response_lower = chatbot_response.lower()

        # Relevance Score: ¿La respuesta es relevante a la consulta?
        query_keywords = set(re.findall(r"\b\w{4,}\b", query_lower))
        response_keywords = set(re.findall(r"\b\w{4,}\b", response_lower))

        if query_keywords:
            overlap = len(query_keywords & response_keywords)
            analysis["relevance_score"] = min(1.0, overlap / len(query_keywords))
        else:
            analysis["relevance_score"] = 0.5  # Neutral si no hay keywords

        # Accuracy Score: ¿La respuesta parece correcta?
        # Detectar indicadores de precisión
        accuracy_indicators = [
            "según",
            "en la base",
            "precio",
            "costo",
            "espesor",
            "autoportancia",
            "fórmula",
            "cálculo",
        ]

        accuracy_count = sum(
            1 for indicator in accuracy_indicators if indicator in response_lower
        )
        analysis["accuracy_score"] = min(1.0, accuracy_count / len(accuracy_indicators))

        # Detectar vaguedad (reduce accuracy)
        vague_phrases = ["no estoy seguro", "creo que", "probablemente", "tal vez"]
        vague_count = sum(1 for phrase in vague_phrases if phrase in response_lower)
        analysis["accuracy_score"] = max(
            0.0, analysis["accuracy_score"] - (vague_count * 0.2)
        )

        # Completeness Score: ¿La respuesta es completa?
        # Verificar si responde a la pregunta
        is_question = "?" in user_query or any(
            word in query_lower
            for word in ["cuanto", "cuál", "qué", "cómo", "dónde", "cuándo"]
        )

        if is_question:
            # Verificar si hay una respuesta directa
            if len(chatbot_response) > 20:  # Respuesta tiene contenido
                analysis["completeness_score"] = 0.7
                if any(
                    word in response_lower
                    for word in ["es", "son", "tiene", "cuesta", "vale"]
                ):
                    analysis["completeness_score"] = 0.9
            else:
                analysis["completeness_score"] = 0.3
        else:
            # Para no-preguntas, verificar si hay información útil
            if len(chatbot_response) > 50:
                analysis["completeness_score"] = 0.8
            else:
                analysis["completeness_score"] = 0.5

        # Sentiment Match: ¿El tono coincide?
        query_positive = any(
            word in query_lower for word in ["gracias", "excelente", "bueno"]
        )
        query_negative = any(
            word in query_lower for word in ["mal", "problema", "error"]
        )

        response_positive = any(
            word in response_lower
            for word in ["gracias", "excelente", "bueno", "perfecto"]
        )
        response_negative = any(
            word in response_lower for word in ["disculpa", "lamento", "problema"]
        )

        if query_positive and response_positive:
            analysis["sentiment_match"] = True
        elif query_negative and not response_negative:
            analysis["sentiment_match"] = False
            analysis["issues"].append("Tono no coincide con consulta negativa")
        else:
            analysis["sentiment_match"] = True  # Neutral match

        # Detectar issues
        if analysis["relevance_score"] < 0.5:
            analysis["issues"].append("Respuesta poco relevante a la consulta")

        if analysis["accuracy_score"] < 0.5:
            analysis["issues"].append("Respuesta puede contener información imprecisa")

        if analysis["completeness_score"] < 0.6:
            analysis["issues"].append("Respuesta incompleta")

        if "no tengo" in response_lower or "no sé" in response_lower:
            analysis["issues"].append("Chatbot indica falta de información")

        # Recomendaciones
        if analysis["relevance_score"] < 0.7:
            analysis["recommendations"].append("Mejorar relevancia de la respuesta")

        if analysis["accuracy_score"] < 0.7:
            analysis["recommendations"].append("Verificar precisión de la información")

        if analysis["completeness_score"] < 0.7:
            analysis["recommendations"].append("Proporcionar respuestas más completas")

        return analysis

    def _generar_resumen_respuestas(self, analyses: List[Dict]) -> Dict:
        """Genera resumen de análisis de respuestas"""
        total = len(analyses)
        if total == 0:
            return {}

        relevance_scores = [a["analysis"]["relevance_score"] for a in analyses]
        accuracy_scores = [a["analysis"]["accuracy_score"] for a in analyses]
        completeness_scores = [a["analysis"]["completeness_score"] for a in analyses]

        avg_relevance = (
            sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        )
        avg_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        )
        avg_completeness = (
            sum(completeness_scores) / len(completeness_scores)
            if completeness_scores
            else 0.0
        )

        sentiment_matches = sum(
            1 for a in analyses if a["analysis"].get("sentiment_match", False)
        )

        total_issues = sum(len(a["analysis"].get("issues", [])) for a in analyses)

        return {
            "total": total,
            "avg_relevance_score": avg_relevance,
            "avg_accuracy_score": avg_accuracy,
            "avg_completeness_score": avg_completeness,
            "sentiment_match_rate": sentiment_matches / total if total > 0 else 0.0,
            "total_issues": total_issues,
            "avg_issues_per_response": total_issues / total if total > 0 else 0.0,
        }

    def generar_reporte_completo(self) -> Dict:
        """
        Genera reporte completo de análisis

        Returns:
            Dict con reporte completo
        """
        print("\n" + "=" * 70)
        print("📋 GENERANDO REPORTE COMPLETO")
        print("=" * 70)

        # 1. Generar tabla de ingestion
        ingestion_summary = self.generar_tabla_ingestion()

        # 2. Analizar cotizaciones
        quote_analysis = self.analizar_cotizaciones()

        # 3. Analizar redes sociales
        social_analysis = self.analizar_redes_sociales()

        # 4. Analizar respuestas
        response_analysis = self.analizar_respuestas()

        # 5. Generar reporte consolidado
        reporte = {
            "timestamp": datetime.now().isoformat(),
            "ingestion_summary": ingestion_summary,
            "quote_analysis": quote_analysis,
            "social_media_analysis": social_analysis,
            "response_analysis": response_analysis,
            "recommendations": self._generar_recomendaciones_generales(
                ingestion_summary, quote_analysis, social_analysis, response_analysis
            ),
        }

        # Guardar reporte
        report_file = (
            self.output_dir
            / f"reporte_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n✅ Reporte guardado en: {report_file}")

        return reporte

    def _generar_recomendaciones_generales(
        self, ingestion, quotes, social, responses
    ) -> List[str]:
        """Genera recomendaciones generales basadas en todos los análisis"""
        recommendations = []

        # Recomendaciones de ingestion
        if ingestion["total_records"] == 0:
            recommendations.append(
                "⚠️  No se encontraron registros para ingestion. Verificar fuentes de datos."
            )

        # Recomendaciones de cotizaciones
        if quotes.get("summary", {}).get("avg_completeness", 1.0) < 0.7:
            recommendations.append(
                "📊 Mejorar completitud de inputs de cotizaciones - muchos inputs están incompletos"
            )

        # Recomendaciones de redes sociales
        social_summary = social.get("summary", {})
        if social_summary.get("response_rate", 0.0) > 0.5:
            recommendations.append(
                "📱 Alta tasa de consultas que requieren respuesta en redes sociales - priorizar atención"
            )

        # Recomendaciones de respuestas
        response_summary = responses.get("summary", {})
        if response_summary.get("avg_relevance_score", 1.0) < 0.7:
            recommendations.append("💬 Mejorar relevancia de respuestas del chatbot")

        if response_summary.get("avg_accuracy_score", 1.0) < 0.7:
            recommendations.append("💬 Mejorar precisión de respuestas del chatbot")

        if response_summary.get("total_issues", 0) > 0:
            recommendations.append(
                f'💬 Revisar {response_summary["total_issues"]} issues detectados en respuestas'
            )

        return recommendations


# ============================================================================
# FUNCIÓN PARA AGENTES DE IA (Function Calling)
# ============================================================================


def get_ingestion_analysis_function_schema() -> Dict:
    """Schema de función para ingestion y análisis completo"""
    return {
        "name": "generar_analisis_ingestion_completo",
        "description": "Genera tabla de ingestion y análisis completo del sistema de chatbot. Analiza cotizaciones, consultas de MercadoLibre/Instagram/Facebook, y revisa respuestas del chatbot contra usuarios.",
        "parameters": {
            "type": "object",
            "properties": {
                "generar_tabla": {
                    "type": "boolean",
                    "description": "Generar tabla de ingestion desde todas las fuentes",
                    "default": True,
                },
                "analizar_cotizaciones": {
                    "type": "boolean",
                    "description": "Analizar inputs de cotizaciones",
                    "default": True,
                },
                "analizar_redes_sociales": {
                    "type": "boolean",
                    "description": "Analizar consultas de redes sociales",
                    "default": True,
                },
                "analizar_respuestas": {
                    "type": "boolean",
                    "description": "Analizar respuestas del chatbot",
                    "default": True,
                },
            },
        },
    }


def generar_analisis_ingestion_completo(
    generar_tabla: bool = True,
    analizar_cotizaciones: bool = True,
    analizar_redes_sociales: bool = True,
    analizar_respuestas: bool = True,
) -> Dict:
    """Función para agentes de IA"""
    agente = AgenteIngestionAnalisis()

    if generar_tabla:
        agente.generar_tabla_ingestion()

    reporte = {}

    if analizar_cotizaciones:
        reporte["quote_analysis"] = agente.analizar_cotizaciones()

    if analizar_redes_sociales:
        reporte["social_analysis"] = agente.analizar_redes_sociales()

    if analizar_respuestas:
        reporte["response_analysis"] = agente.analizar_respuestas()

    return reporte


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agente de Ingestion y Análisis Completo"
    )
    parser.add_argument(
        "--modo",
        choices=["ingestion", "cotizaciones", "redes", "respuestas", "completo"],
        default="completo",
        help="Modo de operación",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="ingestion_database.db",
        help="Ruta a la base de datos",
    )

    args = parser.parse_args()

    agente = AgenteIngestionAnalisis(db_path=args.db_path)

    if args.modo == "ingestion":
        resultado = agente.generar_tabla_ingestion()
    elif args.modo == "cotizaciones":
        resultado = agente.analizar_cotizaciones()
    elif args.modo == "redes":
        resultado = agente.analizar_redes_sociales()
    elif args.modo == "respuestas":
        resultado = agente.analizar_respuestas()
    else:  # completo
        resultado = agente.generar_reporte_completo()

    # Guardar resultado
    output_file = f"ingestion_analysis_{args.modo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Resultado guardado en: {output_file}")
