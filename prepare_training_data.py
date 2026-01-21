#!/usr/bin/env python3
"""
Prepare Training Data for KB Training System
============================================

Helps prepare and structure training data from various sources.
"""

from pathlib import Path
import json
from datetime import datetime
from loguru import logger


def create_training_data_structure():
    """Create training data directory structure"""
    base_dir = Path("training_data")
    
    directories = [
        base_dir / "interactions",
        base_dir / "quotes",
        base_dir / "social_media" / "facebook",
        base_dir / "social_media" / "instagram"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return base_dir


def create_sample_interactions():
    """Create sample interaction data"""
    interactions_dir = Path("training_data/interactions")
    interactions_dir.mkdir(parents=True, exist_ok=True)
    
    sample_interactions = [
        {
            "query": "¿Cuál es el precio de ISODEC EPS 100mm?",
            "response": "El precio de ISODEC EPS 100mm es $46.07 según BMC_Base_Conocimiento_GPT.json",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "is_question": True,
                "platform": "chat",
                "category": "pricing"
            }
        },
        {
            "query": "¿Qué espesor necesito para 6 metros de luz?",
            "response": "Para 6 metros de luz necesitas mínimo 150mm (autoportancia 7.5m), el de 100mm solo aguanta 5.5m",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "is_question": True,
                "platform": "chat",
                "category": "specifications"
            }
        },
        {
            "query": "¿Cuál es la diferencia entre ISODEC e ISOROOF?",
            "response": "ISODEC es para techos pesados (hormigón), ISOROOF es para techos livianos (madera). ISODEC tiene mayor autoportancia.",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "is_question": True,
                "platform": "chat",
                "category": "product_comparison"
            }
        }
    ]
    
    output_file = interactions_dir / "sample_interactions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_interactions, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created sample interactions: {output_file}")
    return sample_interactions


def create_sample_quotes():
    """Create sample quote data"""
    quotes_dir = Path("training_data/quotes")
    quotes_dir.mkdir(parents=True, exist_ok=True)
    
    sample_quotes = [
        {
            "product_code": "ISODEC_EPS_100",
            "product_name": "ISODEC EPS 100mm",
            "price": 46.07,
            "currency": "USD",
            "thickness": "100mm",
            "quantity": 10,
            "total": 460.70,
            "timestamp": datetime.now().isoformat()
        },
        {
            "product_code": "ISOROOF_3G_150",
            "product_name": "ISOROOF 3G 150mm",
            "price": 52.30,
            "currency": "USD",
            "thickness": "150mm",
            "quantity": 5,
            "total": 261.50,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    output_file = quotes_dir / "sample_quotes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_quotes, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created sample quotes: {output_file}")
    return sample_quotes


def create_sample_social_interactions():
    """Create sample social media interaction data"""
    social_dir = Path("training_data/social_media")
    
    sample_facebook = [
        {
            "platform": "facebook",
            "content": "Consulta sobre precio de paneles ISODEC 100mm",
            "timestamp": datetime.now().isoformat(),
            "engagement": {
                "likes": 5,
                "replies": 2
            },
            "metadata": {
                "is_question": True,
                "category": "pricing"
            }
        }
    ]
    
    sample_instagram = [
        {
            "platform": "instagram",
            "content": "¿Qué espesor necesito para mi techo?",
            "timestamp": datetime.now().isoformat(),
            "engagement": {
                "likes": 3,
                "replies": 1
            },
            "metadata": {
                "is_question": True,
                "category": "specifications"
            }
        }
    ]
    
    facebook_dir = social_dir / "facebook"
    instagram_dir = social_dir / "instagram"
    facebook_dir.mkdir(parents=True, exist_ok=True)
    instagram_dir.mkdir(parents=True, exist_ok=True)
    
    facebook_file = facebook_dir / "sample_facebook.json"
    instagram_file = instagram_dir / "sample_instagram.json"
    
    with open(facebook_file, 'w', encoding='utf-8') as f:
        json.dump(sample_facebook, f, indent=2, ensure_ascii=False)
    
    with open(instagram_file, 'w', encoding='utf-8') as f:
        json.dump(sample_instagram, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created sample social interactions: {facebook_file}, {instagram_file}")
    return sample_facebook + sample_instagram


def load_quotes_from_comparison_file():
    """Load quotes from comparison system output if available"""
    comparison_file = Path("comparacion_vendedoras_sistema.json")
    
    if not comparison_file.exists():
        logger.info("Comparison file not found, skipping...")
        return []
    
    try:
        with open(comparison_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        quotes = []
        for presupuesto in data.get('presupuestos', []):
            if isinstance(presupuesto, dict) and 'error' not in presupuesto:
                quote = {
                    "product_code": presupuesto.get('producto', ''),
                    "product_name": presupuesto.get('producto', ''),
                    "price": presupuesto.get('precio_unitario', 0),
                    "currency": "USD",
                    "thickness": presupuesto.get('espesor', ''),
                    "quantity": presupuesto.get('cantidad', 0),
                    "timestamp": datetime.now().isoformat()
                }
                quotes.append(quote)
        
        if quotes:
            quotes_dir = Path("training_data/quotes")
            quotes_dir.mkdir(parents=True, exist_ok=True)
            output_file = quotes_dir / "from_comparison.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(quotes, f, indent=2, ensure_ascii=False)
            logger.info(f"Loaded {len(quotes)} quotes from comparison file")
        
        return quotes
    except Exception as e:
        logger.error(f"Error loading comparison file: {e}")
        return []


def main():
    """Main function to prepare training data"""
    print("=" * 70)
    print("🚀 Preparing Training Data for KB Training System")
    print("=" * 70)
    
    # Create directory structure
    print("\n📁 Creating directory structure...")
    create_training_data_structure()
    
    # Create sample data
    print("\n📝 Creating sample data...")
    sample_interactions = create_sample_interactions()
    sample_quotes = create_sample_quotes()
    sample_social = create_sample_social_interactions()
    
    # Try to load from comparison file
    print("\n📊 Loading quotes from comparison system...")
    comparison_quotes = load_quotes_from_comparison_file()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Training Data Preparation Complete!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Sample Interactions: {len(sample_interactions)}")
    print(f"   Sample Quotes: {len(sample_quotes)}")
    print(f"   Sample Social: {len(sample_social)}")
    print(f"   Quotes from Comparison: {len(comparison_quotes)}")
    
    print(f"\n📁 Data Location:")
    print(f"   Interactions: training_data/interactions/")
    print(f"   Quotes: training_data/quotes/")
    print(f"   Social Media: training_data/social_media/")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review sample data in training_data/ directory")
    print(f"   2. Add your own data following the same format")
    print(f"   3. Run: python3 integrate_training_system.py")
    print(f"   4. Check the generated report")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
