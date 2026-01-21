"""
GPT Configuration Generator
===========================

Generates optimal GPT configurations based on knowledge base analysis.
Specialized in GPT creator workflows.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from loguru import logger


class GPTConfigGenerator:
    """
    Generates GPT configurations optimized for knowledge base structure.
    """
    
    def __init__(self, knowledge_base_path: str):
        """
        Initialize generator
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.kb_path = Path(knowledge_base_path)
    
    def generate_config(
        self,
        gpt_name: str,
        use_case: str = "general",
        kb_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate complete GPT configuration.
        
        Args:
            gpt_name: Name for the GPT
            use_case: Use case type (general, quotation, assistant, etc.)
            kb_analysis: Optional knowledge base analysis
            
        Returns:
            Complete GPT configuration
        """
        logger.info(f"Generating GPT configuration: {gpt_name} ({use_case})")
        
        # Generate system instructions
        system_instructions = self._generate_system_instructions(
            gpt_name, use_case, kb_analysis
        )
        
        # Generate knowledge base configuration
        kb_config = self._generate_kb_config(kb_analysis)
        
        # Generate capabilities
        capabilities = self._generate_capabilities(use_case)
        
        # Generate actions (if applicable)
        actions = self._generate_actions(use_case)
        
        config = {
            "name": gpt_name,
            "description": self._generate_description(gpt_name, use_case),
            "instructions": system_instructions,
            "knowledge_base": kb_config,
            "capabilities": capabilities,
            "actions": actions,
            "metadata": {
                "created": datetime.now().isoformat(),
                "use_case": use_case,
                "version": "1.0.0"
            }
        }
        
        return config
    
    def _generate_system_instructions(
        self,
        gpt_name: str,
        use_case: str,
        kb_analysis: Optional[Dict]
    ) -> str:
        """Generate system instructions for GPT"""
        
        base_instructions = f"""You are {gpt_name}, a specialized GPT assistant.

## Knowledge Base Hierarchy

You have access to a hierarchical knowledge base with the following structure:

### Level 1 (Master) - Source of Truth
- **ALWAYS use this first** for prices, formulas, and specifications
- Files: BMC_Base_Conocimiento_GPT.json, BMC_Base_Conocimiento_GPT-2.json
- This is the authoritative source for all technical and commercial data

### Level 2 (Validation)
- Use for cross-reference and validation only
- File: BMC_Base_Unificada_v4.json
- Do NOT use this as primary source for responses

### Level 3 (Dynamic)
- Use for price updates and stock status
- File: panelin_truth_bmcuruguay_web_only_v2.json
- Always verify against Level 1

### Level 4 (Support)
- Supplementary information only
- Files: RTF files, CSV files, Markdown files

## Source of Truth Rules

1. **ALWAYS consult Level 1 first** for any price, formula, or specification query
2. If Level 1 doesn't have the information, check Level 2 for validation
3. Use Level 3 for recent price updates, but verify against Level 1
4. When conflicts exist, Level 1 always takes precedence
5. Document which source you used in your response

## Response Guidelines

- Be accurate and technical
- Cite your sources (which knowledge base level you used)
- If information conflicts, use Level 1 and note the conflict
- Provide detailed technical specifications when available
- Include formulas and calculations when relevant
"""
        
        # Add use-case specific instructions
        if use_case == "quotation":
            base_instructions += """

## Quotation Process

When generating quotations:
1. Identify products from Level 1 knowledge base
2. Validate technical specifications (autoportancia, espesor, etc.)
3. Use formulas from Level 1 for calculations
4. Apply pricing from Level 1 (verify with Level 3 for updates)
5. Present detailed breakdown with materials, costs, and IVA
"""
        elif use_case == "assistant":
            base_instructions += """

## Assistant Capabilities

- Multi-step reasoning for complex queries
- Technical validation of specifications
- Hierarchical knowledge base access
- Conflict resolution using Level 1 as source of truth
- Personalized responses based on context
"""
        
        return base_instructions
    
    def _generate_kb_config(self, kb_analysis: Optional[Dict]) -> Dict[str, Any]:
        """Generate knowledge base configuration"""
        config = {
            "hierarchy": {
                "level_1_master": [
                    "BMC_Base_Conocimiento_GPT.json",
                    "BMC_Base_Conocimiento_GPT-2.json"
                ],
                "level_2_validation": [
                    "BMC_Base_Unificada_v4.json"
                ],
                "level_3_dynamic": [
                    "panelin_truth_bmcuruguay_web_only_v2.json"
                ],
                "level_4_support": [
                    "Aleros -2.rtf",
                    "panelin_truth_bmcuruguay_catalog_v2_index.csv"
                ]
            },
            "source_of_truth": "level_1_master",
            "conflict_resolution": "hierarchical",
            "retrieval_strategy": {
                "primary": "semantic_search",
                "fallback": "keyword_search",
                "reranking": "source_priority"
            }
        }
        
        if kb_analysis:
            files_found = kb_analysis.get("files_found", [])
            existing_files = [f for f in files_found if f.get("exists")]
            config["files_available"] = [f["name"] for f in existing_files]
        
        return config
    
    def _generate_capabilities(self, use_case: str) -> Dict[str, Any]:
        """Generate capabilities configuration"""
        base_capabilities = {
            "web_browsing": False,
            "code_interpreter": True,
            "image_generation": False,
            "file_upload": True
        }
        
        if use_case == "quotation":
            base_capabilities["code_interpreter"] = True  # For calculations
        
        return base_capabilities
    
    def _generate_actions(self, use_case: str) -> List[Dict]:
        """Generate actions configuration"""
        actions = []
        
        if use_case == "quotation":
            actions.append({
                "name": "generate_quotation",
                "description": "Generate a complete quotation with product identification, validation, and pricing",
                "parameters": {
                    "products": {
                        "type": "array",
                        "description": "List of products to quote"
                    },
                    "specifications": {
                        "type": "object",
                        "description": "Technical specifications"
                    }
                }
            })
        
        return actions
    
    def _generate_description(self, gpt_name: str, use_case: str) -> str:
        """Generate GPT description"""
        descriptions = {
            "general": f"{gpt_name} - Specialized GPT assistant with hierarchical knowledge base access",
            "quotation": f"{gpt_name} - Quotation system with 5-phase process: identification, validation, data retrieval, calculations, and detailed presentation",
            "assistant": f"{gpt_name} - Intelligent assistant with multi-step reasoning and technical validation capabilities"
        }
        
        return descriptions.get(use_case, descriptions["general"])
    
    def generate_opal_config(self, gpt_name: str, use_case: str) -> Dict[str, Any]:
        """
        Generate Opal app configuration for Google Labs.
        
        Args:
            gpt_name: Name for the GPT
            use_case: Use case type
            
        Returns:
            Opal app configuration
        """
        logger.info(f"Generating Opal config: {gpt_name} ({use_case})")
        
        gpt_config = self.generate_config(gpt_name, use_case)
        
        opal_config = {
            "opal_version": "1.0",
            "asset_type": "gpt_knowledge_base_configuration",
            "metadata": {
                "created": datetime.now().isoformat(),
                "gpt_name": gpt_name,
                "use_case": use_case,
                "version": "1.0.0"
            },
            "system_instructions": {
                "main_agent": gpt_config["instructions"],
                "capabilities": list(gpt_config["capabilities"].keys()),
                "knowledge_base_hierarchy": gpt_config["knowledge_base"]["hierarchy"]
            },
            "knowledge_base": gpt_config["knowledge_base"],
            "workflows": self._generate_workflows(use_case),
            "tools": {
                "available_tools": [
                    "code_interpreter",
                    "file_upload",
                    "knowledge_base_access"
                ]
            }
        }
        
        return opal_config
    
    def _generate_workflows(self, use_case: str) -> List[Dict]:
        """Generate workflows for Opal config"""
        workflows = []
        
        if use_case == "quotation":
            workflows.append({
                "workflow_id": "quotation_process",
                "name": "5-Phase Quotation Process",
                "description": "Complete quotation workflow with validation and calculations",
                "nodes": [
                    {
                        "id": "identify_products",
                        "type": "process",
                        "name": "Identify Products"
                    },
                    {
                        "id": "validate_technical",
                        "type": "validate",
                        "name": "Technical Validation"
                    },
                    {
                        "id": "retrieve_data",
                        "type": "retrieve",
                        "name": "Retrieve from Knowledge Base"
                    },
                    {
                        "id": "calculate",
                        "type": "calculate",
                        "name": "Calculate with Formulas"
                    },
                    {
                        "id": "present",
                        "type": "output",
                        "name": "Present Quotation"
                    }
                ]
            })
        
        return workflows
