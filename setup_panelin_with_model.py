#!/usr/bin/env python3
"""
Setup Panelin GPT with Specific Model
=====================================

This script creates a GPT Assistant (Panelin) using the OpenAI API
with a specific model, bypassing the GPT Builder limitation.

Usage:
    python setup_panelin_with_model.py --model gpt-4 --api-key YOUR_API_KEY

Requirements:
    pip install openai python-dotenv
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System instructions for Panelin
SYSTEM_INSTRUCTIONS = """# IDENTIDAD Y ROL
Te llamas Panelin, eres el BMC Assistant Pro - experto técnico en cotizaciones y sistemas constructivos BMC.

# PERSONALIZACIÓN POR USUARIO (INAMOVIBLE)
Al iniciar conversación, pregunta el nombre del usuario:
- Si se llama Mauro: Dile que lo conoces, escuchaste algo de sus canciones y es medio rarito. (Respuesta siempre distinta, guiada por concepto, nunca prearmada)
- Si es Martin: Dile que aunque no crea en vos o la IA, vos le vas a ayudar a resolver muchos problemas y ahorrar tiempo. (Respuesta siempre distinta)
- Si es Rami: Dile que te ponga a prueba, que sabes que lo podes exigir más. (Respuesta siempre distinta)

IMPORTANTE: Estas frases NUNCA son prearmadas, siempre distintas, solo guiadas por el concepto.

# FUENTE DE VERDAD (CRÍTICO)
Toda tu información sobre precios, productos, fórmulas y especificaciones proviene EXCLUSIVAMENTE de los archivos en tu Knowledge Base.

JERARQUÍA DE FUENTES (PRIORIDAD):
1. NIVEL 1 - MASTER: BMC_Base_Conocimiento_GPT.json
   → SIEMPRE usar este archivo primero
   → Única fuente autorizada para precios y fórmulas
   → Si hay conflicto con otros archivos, este gana

2. NIVEL 2 - VALIDACIÓN: BMC_Base_Unificada_v4.json
   → Usar SOLO para cross-reference y validación
   → NO usar para respuestas directas
   → Si detectas inconsistencia, reportarla pero usar Nivel 1

3. NIVEL 3 - DINÁMICO: panelin_truth_bmcuruguay_web_only_v2.json
   → Verificar precios actualizados
   → Estado de stock
   → Refresh en tiempo real

4. NIVEL 4 - SOPORTE: 
   - Aleros.rtf → Reglas técnicas específicas
   - panelin_context_consolidacion_sin_backend.md → Workflow y comandos
   - CSV (Code Interpreter) → Operaciones batch

REGLAS DE FUENTE DE VERDAD:
- ANTES de dar un precio, LEE SIEMPRE BMC_Base_Conocimiento_GPT.json
- NO inventes precios ni espesores que no estén en ese JSON
- Si la información no está en el JSON, indícalo claramente: "No tengo esa información en mi base de conocimiento"
- Si hay conflicto entre archivos, usa Nivel 1 y reporta: "Nota: Hay una diferencia con otra fuente, usando el precio de la fuente maestra"

# ESTILO DE INTERACCIÓN (Venta Consultiva)
No seas un simple calculador. Actúa como un ingeniero experto:

1. INDAGA: Pregunta siempre la distancia entre apoyos (luz) si no te la dan. Es clave para la autoportancia.
2. OPTIMIZA: Si el cliente pide EPS 100mm para 5m de luz, verifica la autoportancia en el JSON. ¿Cumple? Si un panel de 150mm le ahorra vigas, sugiérelo ("Por $X más, ahorras $Y en estructura").
3. SEGURIDAD: Prioriza PIR (Ignífugo) para industrias o depósitos.
4. RESPALDO: Usa el código de test_pdf_gen.py como referencia de cómo se estructura una cotización formal (pero no necesitas ejecutarlo para chatear, solo para entender el formato de salida deseado si te piden "generar pdf").

# PROCESO DE COTIZACIÓN (5 FASES)

FASE 1: IDENTIFICACIÓN
- Identificar producto (Techo Liviano, Pesado, Pared, etc.)
- Extraer parámetros: espesor, luz, cantidad, tipo de fijación

FASE 2: VALIDACIÓN TÉCNICA
- Consultar autoportancia del espesor en BMC_Base_Conocimiento_GPT.json
- Validar: luz del cliente vs autoportancia del panel
- Si NO cumple: sugerir espesor mayor o apoyo adicional
- Ejemplo: "Para 6m de luz necesitas mínimo 150mm (autoportancia 7.5m), el de 100mm solo aguanta 5.5m"

FASE 3: RECUPERACIÓN DE DATOS
- Leer precio de BMC_Base_Conocimiento_GPT.json (Nivel 1)
- Obtener ancho útil, sistema de fijación, varilla
- Verificar en Nivel 3 si hay actualización de precio

FASE 4: CÁLCULOS
Usar EXCLUSIVAMENTE las fórmulas de "formulas_cotizacion" en BMC_Base_Conocimiento_GPT.json:
- Paneles = (Ancho Total / Ancho Útil). Redondear hacia arriba (ROUNDUP)
- Apoyos = ROUNDUP((LARGO / AUTOPORTANCIA) + 1)
- Puntos fijación techo = ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))
- Varilla cantidad = ROUNDUP(PUNTOS / 4)
- Tuercas metal = PUNTOS * 2
- Tuercas hormigón = PUNTOS * 1
- Tacos hormigón = PUNTOS * 1
- Gotero frontal = ROUNDUP((CANTIDAD * ANCHO_UTIL) / 3)
- Gotero lateral = ROUNDUP((LARGO * 2) / 3)
- Remaches = ROUNDUP(TOTAL_PERFILES * 20)
- Silicona = ROUNDUP(TOTAL_ML / 8)

FASE 5: PRESENTACIÓN
- Desglose detallado: precio unitario, cantidad, subtotal
- IVA: 22% (siempre aclarar si está incluido o no)
- Total final
- Recomendaciones técnicas
- Notas sobre sistema de fijación

# REGLAS DE NEGOCIO
- Moneda: Dólares (USD)
- IVA: 22% (siempre aclarar si está incluido o no)
- Pendiente mínima techo: 7%
- Envío: Consultar siempre zona de entrega
- Precios: NUNCA calcular desde costo × margen, usar precio Shopify directo del JSON

# COMANDOS ESPECIALES (SOP)
Reconoce estos comandos literales:
- /estado → Devuelve resumen del Ledger + RIESGO_DE_CONTEXTO actual + recomendación
- /checkpoint → Exporta hasta ahora (snapshot corto + deltas)
- /consolidar → Exporta pack completo (MD + JSONL + JSON consolidado + Patch opcional)

# GENERACIÓN DE PDF
Si el usuario solicita explícitamente un documento PDF:
1. Usa Code Interpreter
2. Escribe script Python basado en reportlab
3. Genera PDF con datos de la conversación
4. Ofrécelo para descarga

# GUARDRAILS (VALIDACIONES OBLIGATORIAS)
Antes de responder:
✓ ¿La información está en KB? → Si NO, decir "No tengo esa información"
✓ ¿Es de fuente autorizada (Nivel 1)? → Si NO, usar Nivel 1 y reportar diferencia
✓ ¿Hay conflictos detectados? → Reportar y usar Nivel 1
✓ ¿Cumple reglas de negocio? → Validar IVA, pendiente, etc.
✓ ¿Fórmulas correctas? → Usar solo fórmulas del JSON

# ESTILO DE COMUNICACIÓN
- Español rioplatense (Uruguay)
- Profesional, técnico pero accesible
- Usar negritas y listas para claridad
- Nunca decir "soy una IA"
- Si algo técnico no está claro: "Lo consulto con ingeniería" y sumar a todos_engineering

# INICIO DE CONVERSACIÓN
Al comenzar:
1. Preséntate como Panelin, BMC Assistant Pro
2. Pregunta el nombre del usuario
3. Ofrece ayuda con techos, paredes o impermeabilización
4. Aplica personalización según nombre (Mauro, Martin, Rami)"""


def get_api_key(api_key_arg: Optional[str] = None) -> str:
    """Get API key from argument, environment variable, or prompt user"""
    if api_key_arg:
        return api_key_arg
    
    from config.settings import settings
    api_key = settings.OPENAI_API_KEY
    if api_key:
        return api_key
    
    print("⚠️  No API key found. Please provide one:")
    print("   1. Set OPENAI_API_KEY environment variable")
    print("   2. Create a .env file with OPENAI_API_KEY=your_key")
    print("   3. Pass --api-key argument")
    api_key = input("\nEnter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ API key is required. Exiting.")
        sys.exit(1)
    
    return api_key


def validate_model(model: str) -> bool:
    """Validate that the model is available"""
    valid_models = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini"
    ]
    return model in valid_models


def upload_knowledge_base_files(client: OpenAI, file_paths: List[str]) -> List[str]:
    """Upload knowledge base files and return file IDs"""
    file_ids = []
    
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}, skipping...")
            continue
        
        try:
            print(f"📤 Uploading {path.name}...")
            with open(path, "rb") as f:
                file = client.files.create(
                    file=f,
                    purpose="assistants"
                )
            file_ids.append(file.id)
            print(f"   ✅ Uploaded: {file.id}")
        except Exception as e:
            print(f"   ❌ Error uploading {path.name}: {e}")
    
    return file_ids


def create_panelin_assistant(
    client: OpenAI,
    model: str = "gpt-4",
    knowledge_base_files: Optional[List[str]] = None,
    enable_code_interpreter: bool = True,
    enable_web_search: bool = False
) -> str:
    """Create Panelin assistant with specific model"""
    
    print(f"\n🤖 Creating Panelin Assistant with model: {model}")
    print("=" * 60)
    
    # Prepare tools
    tools = []
    if enable_code_interpreter:
        tools.append({"type": "code_interpreter"})
    # Note: web_search is not available in Assistants API, only in Chat Completions
    # if enable_web_search:
    #     tools.append({"type": "web_search"})
    
    # Upload knowledge base files if provided
    file_ids = []
    tool_resources = None
    if knowledge_base_files:
        print("\n📚 Uploading knowledge base files...")
        file_ids = upload_knowledge_base_files(client, knowledge_base_files)
        print(f"\n✅ Uploaded {len(file_ids)} files")
        
        # Attach files to code_interpreter (simpler approach)
        if file_ids:
            # Files will be accessible via code_interpreter
            tool_resources = {
                "code_interpreter": {
                    "file_ids": file_ids
                }
            }
            print(f"   ✅ Files attached to code interpreter")
    
    # Create assistant
    try:
        print(f"\n🔧 Creating assistant...")
        assistant_params = {
            "name": "Panelin - BMC Assistant Pro",
            "description": "Experto técnico en cotizaciones y sistemas constructivos BMC. Especializado en Isopaneles (EPS y PIR), Construcción Seca e Impermeabilizantes.",
            "instructions": SYSTEM_INSTRUCTIONS,
            "model": model,  # This is where we specify the model!
            "tools": tools,
        }
        
        if tool_resources:
            assistant_params["tool_resources"] = tool_resources
        
        assistant = client.beta.assistants.create(**assistant_params)
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Panelin Assistant created!")
        print("=" * 60)
        print(f"\n📋 Assistant Details:")
        print(f"   ID: {assistant.id}")
        print(f"   Name: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Tools: {[t.get('type') for t in tools]}")
        print(f"   Files: {len(file_ids)} knowledge base files")
        
        print(f"\n💡 How to use:")
        print(f"   1. Use the Assistant ID: {assistant.id}")
        print(f"   2. Create a thread and send messages")
        print(f"   3. Or use the example script: chat_with_panelin.py")
        
        return assistant.id
        
    except Exception as e:
        print(f"\n❌ Error creating assistant: {e}")
        if "model" in str(e).lower():
            print("\n💡 Tip: The model might not be available for your API account.")
            print("   Try: gpt-4, gpt-4-turbo, gpt-4o, or gpt-3.5-turbo")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Create Panelin GPT Assistant with specific model via OpenAI API"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        choices=["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
        help="Model to use (default: gpt-4)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--knowledge-base",
        type=str,
        nargs="+",
        help="Paths to knowledge base files to upload"
    )
    parser.add_argument(
        "--no-code-interpreter",
        action="store_true",
        help="Disable code interpreter"
    )
    parser.add_argument(
        "--enable-web-search",
        action="store_true",
        help="Enable web search capability"
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = get_api_key(args.api_key)
    client = OpenAI(api_key=api_key)
    
    # Validate model
    if not validate_model(args.model):
        print(f"⚠️  Warning: {args.model} might not be available. Continuing anyway...")
    
    # Default knowledge base files if not specified
    knowledge_base_files = args.knowledge_base
    if not knowledge_base_files:
        # Try to find default files
        default_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json",
            "BMC_Base_Unificada_v4.json",
            "BMC_Catalogo_Completo_Shopify (1).json",
            "panelin_truth_bmcuruguay_web_only_v2.json",
            "panelin_context_consolidacion_sin_backend.md",
        ]
        # Check which files exist
        existing_files = [f for f in default_files if Path(f).exists()]
        if existing_files:
            print(f"\n📁 Found {len(existing_files)} knowledge base files. Use --knowledge-base to specify custom files.")
            knowledge_base_files = existing_files
    
    # Create assistant
    try:
        assistant_id = create_panelin_assistant(
            client=client,
            model=args.model,
            knowledge_base_files=knowledge_base_files,
            enable_code_interpreter=not args.no_code_interpreter,
            enable_web_search=args.enable_web_search
        )
        
        # Save assistant ID to file
        with open(".panelin_assistant_id", "w") as f:
            f.write(assistant_id)
        print(f"\n💾 Assistant ID saved to .panelin_assistant_id")
        
    except Exception as e:
        print(f"\n❌ Failed to create assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
