#!/usr/bin/env python3
"""
Script para verificar la configuración del agente de ingestion
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
print("=" * 70)

# Verificar .env existe
env_file = Path(".env")
if env_file.exists():
    print("\n✅ Archivo .env encontrado")
else:
    print("\n⚠️  Archivo .env no encontrado")
    print("   Crear archivo .env con las variables necesarias")

# MongoDB
print("\n📊 MongoDB:")
    from config.settings import settings
    mongodb_conn = settings.MONGODB_URI
    mongodb_db = settings.MONGODB_DB

if mongodb_conn:
    print(f"   ✅ MONGODB_CONNECTION_STRING configurado")
    # Intentar conectar
    try:
        from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient
        client = MongoDBClient()
        if client.db:
            print(f"   ✅ Conectado a MongoDB")
            print(f"   ✅ Base de datos: {client.database_name}")
            collections = client.list_collections()
            if collections:
                print(f"   ✅ Colecciones encontradas: {len(collections)}")
                for col in collections[:5]:
                    print(f"      - {col}")
            else:
                print(f"   ⚠️  No hay colecciones en la base de datos")
        else:
            print(f"   ❌ No se pudo conectar a MongoDB")
            print(f"   ⚠️  Verificar connection string")
    except ImportError:
        print(f"   ⚠️  pymongo no instalado: pip install pymongo")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print(f"   ⚠️  MONGODB_CONNECTION_STRING no configurado")

# Facebook
print("\n📘 Facebook:")
    from config.settings import settings
    fb_app_id = os.getenv("FACEBOOK_APP_ID")
    fb_token = settings.FB_PAGE_ACCESS_TOKEN
    fb_page_id = os.getenv("FACEBOOK_PAGE_ID")

if fb_app_id and fb_token and fb_page_id:
    print(f"   ✅ Facebook API configurado")
else:
    print(f"   ⚠️  Facebook API no configurado")
    if not fb_app_id:
        print(f"      - FACEBOOK_APP_ID faltante")
    if not fb_token:
        print(f"      - FACEBOOK_PAGE_ACCESS_TOKEN faltante")
    if not fb_page_id:
        print(f"      - FACEBOOK_PAGE_ID faltante")

# Instagram
print("\n📷 Instagram:")
    ig_app_id = os.getenv("INSTAGRAM_APP_ID")
    ig_token = settings.INSTAGRAM_ACCESS_TOKEN
    ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

if ig_app_id and ig_token and ig_account_id:
    print(f"   ✅ Instagram API configurado")
else:
    print(f"   ⚠️  Instagram API no configurado")
    if not ig_app_id:
        print(f"      - INSTAGRAM_APP_ID faltante")
    if not ig_token:
        print(f"      - INSTAGRAM_ACCESS_TOKEN faltante")
    if not ig_account_id:
        print(f"      - INSTAGRAM_BUSINESS_ACCOUNT_ID faltante")

# MercadoLibre
print("\n🛒 MercadoLibre:")
ml_token = os.getenv("MERCADOLIBRE_ACCESS_TOKEN")
ml_user_id = os.getenv("MERCADOLIBRE_USER_ID")

if ml_token and ml_user_id:
    print(f"   ✅ MercadoLibre API configurado")
else:
    print(f"   ⚠️  MercadoLibre API no configurado")
    if not ml_token:
        print(f"      - MERCADOLIBRE_ACCESS_TOKEN faltante")
    if not ml_user_id:
        print(f"      - MERCADOLIBRE_USER_ID faltante")

# Verificar archivos de datos
print("\n📁 Archivos de Datos:")

# CSV de cotizaciones
csv_path = "/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv"
if Path(csv_path).exists():
    print(f"   ✅ CSV de cotizaciones encontrado")
else:
    print(f"   ⚠️  CSV de cotizaciones no encontrado: {csv_path}")

# Training data
training_dir = Path("training_data")
if training_dir.exists():
    print(f"   ✅ Directorio training_data existe")
    
    # MercadoLibre
    ml_dir = training_dir / "mercadolibre"
    if ml_dir.exists():
        ml_files = list(ml_dir.glob("*.json"))
        if ml_files:
            print(f"   ✅ {len(ml_files)} archivos JSON de MercadoLibre")
        else:
            print(f"   ⚠️  No hay archivos JSON en mercadolibre/")
    else:
        print(f"   ⚠️  Directorio mercadolibre/ no existe")
    
    # Social media
    social_dir = training_dir / "social_media"
    if social_dir.exists():
        fb_files = list((social_dir / "facebook").glob("*.json")) if (social_dir / "facebook").exists() else []
        ig_files = list((social_dir / "instagram").glob("*.json")) if (social_dir / "instagram").exists() else []
        
        if fb_files:
            print(f"   ✅ {len(fb_files)} archivos JSON de Facebook")
        if ig_files:
            print(f"   ✅ {len(ig_files)} archivos JSON de Instagram")
else:
    print(f"   ⚠️  Directorio training_data no existe")

# Base de datos
print("\n💾 Base de Datos:")
db_path = Path("ingestion_database.db")
if db_path.exists():
    size = db_path.stat().st_size / 1024  # KB
    print(f"   ✅ Base de datos existe ({size:.1f} KB)")
    
    # Verificar tablas
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   ✅ Tablas: {', '.join(tables)}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM ingestion_table")
        count = cursor.fetchone()[0]
        print(f"   ✅ Registros en ingestion_table: {count}")
        conn.close()
    except Exception as e:
        print(f"   ⚠️  Error leyendo base de datos: {e}")
else:
    print(f"   ⚠️  Base de datos no existe (se creará en primera ejecución)")

# Reportes
print("\n📊 Reportes:")
report_dir = Path("ingestion_analysis_output")
if report_dir.exists():
    reports = list(report_dir.glob("reporte_completo_*.json"))
    if reports:
        latest = max(reports, key=lambda p: p.stat().st_mtime)
        print(f"   ✅ {len(reports)} reportes encontrados")
        print(f"   ✅ Más reciente: {latest.name}")
    else:
        print(f"   ⚠️  No hay reportes generados")
else:
    print(f"   ⚠️  Directorio de reportes no existe (se creará en primera ejecución)")

print("\n" + "=" * 70)
print("✅ Verificación completada")
print("=" * 70)
