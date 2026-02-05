#!/usr/bin/env python3
"""
Setup KB Indexing Expert Agent
==============================

Sets up the KB Indexing Expert Agent for GPT OpenAI Actions API.
Creates an OpenAI Assistant with optimized KB indexing functions.
"""

import os
import json
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai not installed. Install with: pip install openai")
    exit(1)

from agente_kb_indexing import get_all_kb_function_schemas


def setup_openai_kb_agent(api_key: Optional[str] = None) -> Optional[dict]:
    """
    Setup KB Indexing Expert Agent as OpenAI Assistant
    
    Args:
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
    
    Returns:
        Assistant configuration dict
    """
    from config.settings import settings
    api_key = api_key or settings.OPENAI_API_KEY
    if not api_key:
        print("❌ OpenAI API key required. Set OPENAI_API_KEY env var or pass as argument.")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Load agent config
        config_path = Path(__file__).parent / "gpt_configs" / "KB_Indexing_Expert_Agent_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Get all function schemas
        function_schemas = get_all_kb_function_schemas()
        
        # Create assistant
        assistant = client.beta.assistants.create(
            name=config["name"],
            instructions=config["instructions"],
            model=config["model"],
            tools=[{"type": "function", "function": schema} for schema in function_schemas],
            tool_resources={
                "code_interpreter": {
                    "file_ids": []  # Can add KB files here if needed
                }
            }
        )
        
        print("✅ KB Indexing Expert Agent created successfully!")
        print(f"   Name: {assistant.name}")
        print(f"   ID: {assistant.id}")
        print(f"   Model: {assistant.model}")
        print(f"   Functions: {len(function_schemas)}")
        print("\n📋 Available Functions:")
        for schema in function_schemas:
            print(f"   - {schema['name']}: {schema['description'][:60]}...")
        
        # Save assistant ID
        id_file = Path(__file__).parent / ".kb_indexing_assistant_id"
        with open(id_file, 'w') as f:
            f.write(assistant.id)
        
        print(f"\n💾 Assistant ID saved to: {id_file}")
        
        # Save full config
        output_config = {
            "assistant_id": assistant.id,
            "name": assistant.name,
            "model": assistant.model,
            "functions": [schema["name"] for schema in function_schemas],
            "created_at": assistant.created_at,
            "config_file": str(config_path)
        }
        
        output_file = Path(__file__).parent / "gpt_configs" / "KB_Indexing_Expert_Agent_setup.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_config, f, indent=2)
        
        print(f"💾 Full configuration saved to: {output_file}")
        
        print("\n📝 Usage Example:")
        print("   from agente_kb_indexing import search_knowledge_base")
        print("   result = search_knowledge_base('ISODEC 100mm price')")
        print("   print(result)")
        
        return output_config
        
    except Exception as e:
        print(f"❌ Error setting up agent: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_kb_functions():
    """Test KB indexing functions locally"""
    print("🧪 Testing KB Indexing Functions...\n")
    
    from agente_kb_indexing import (
        search_knowledge_base,
        get_product_information,
        get_formula,
        validate_kb_health,
        get_kb_metadata,
        build_kb_index
    )
    
    # Test 1: Build index
    print("1. Building KB index...")
    index_result = build_kb_index()
    print(f"   ✅ Index built: {index_result.get('total_entries', 0)} entries")
    
    # Test 2: Search KB
    print("\n2. Testing search...")
    search_result = search_knowledge_base("ISODEC 100mm", level_priority=1, max_results=5)
    print(f"   ✅ Found {search_result.get('total_matches', 0)} results")
    
    # Test 3: Get product info
    print("\n3. Testing product info...")
    product_result = get_product_information("ISODEC EPS", "100")
    if "error" not in product_result:
        print(f"   ✅ Product found: {product_result.get('product', 'N/A')}")
    else:
        print(f"   ⚠️  {product_result.get('error', 'Unknown error')}")
    
    # Test 4: Get formula
    print("\n4. Testing formula retrieval...")
    formula_result = get_formula("cantidad_paneles")
    if "error" not in formula_result:
        print(f"   ✅ Formula found: {formula_result.get('formula', 'N/A')}")
    else:
        print(f"   ⚠️  {formula_result.get('error', 'Unknown error')}")
    
    # Test 5: Health check
    print("\n5. Testing health validation...")
    health_result = validate_kb_health()
    print(f"   ✅ KB Status: {health_result.get('status', 'unknown')}")
    
    # Test 6: Metadata
    print("\n6. Testing metadata retrieval...")
    metadata_result = get_kb_metadata()
    print(f"   ✅ Metadata retrieved: {len(metadata_result.get('files', {}))} files")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_kb_functions()
    else:
        print("🚀 Setting up KB Indexing Expert Agent for GPT OpenAI Actions...\n")
        setup_openai_kb_agent()
        print("\n💡 Tip: Run 'python setup_kb_indexing_agent.py test' to test functions locally")
