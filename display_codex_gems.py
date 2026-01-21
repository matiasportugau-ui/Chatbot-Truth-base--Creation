#!/usr/bin/env python3
"""Display Codex Generated Gems in a readable format"""

import json
from pathlib import Path

def main():
    json_file = Path("codex_generated_gems.json")
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('=' * 80)
    print('🚀 CODEX GENERATED GEMS - READY FOR GOOGLE LABS')
    print('=' * 80)
    print(f'\n📊 Total Gems Generated: {data["total_gems"]}')
    print(f'📅 Codex Analysis Timestamp: {data["codex_timestamp"]}')
    
    print('\n✅ Codex Insights Used:')
    for insight, used in data['codex_insights_used'].items():
        status = '✅' if used else '❌'
        print(f'   {status} {insight}')
    
    print('\n' + '=' * 80)
    print('📋 GEM DESCRIPTIONS (Copy to Google Labs)')
    print('=' * 80)
    
    for i, gem_item in enumerate(data['gems'], 1):
        print(f'\n\n{"="*80}')
        print(f'{i}. {gem_item["name"]} ({gem_item["type"]})')
        print('=' * 80)
        
        gem = gem_item.get('gem', {})
        if gem.get('descripcion_gem'):
            desc = gem['descripcion_gem']
            print('\n📝 Description for Google Labs:')
            print('-' * 80)
            print(desc)
            
            workflow = gem.get('workflow', {})
            validation = workflow.get('validacion', {})
            print(f'\n✅ Valid: {gem.get("valido", False)}')
            print(f'📊 Workflow Nodes: {validation.get("total_nodos", 0)}')
            if validation.get('errores'):
                print(f'⚠️  Errors: {len(validation.get("errores", []))}')
                for error in validation['errores']:
                    print(f'   - {error}')
        else:
            print('⚠️  No description available')
    
    print('\n' + '=' * 80)
    print('💡 NEXT STEPS:')
    print('=' * 80)
    print('1. Copy each gem_description above')
    print('2. Go to gemini.google.com')
    print('3. Click "Gems" → "New Gem"')
    print('4. Paste the description')
    print('5. Wait for Gemini to generate the workflow')
    print('6. Test and refine!')
    print('=' * 80)

if __name__ == "__main__":
    main()
