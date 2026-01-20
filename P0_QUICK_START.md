# 🚀 P0 Quick Start Guide
## Critical Priority Items - Ready to Execute

**Start Date:** [To be filled]  
**Target Completion:** Week 2  
**Team:** Backend Developer + QA Engineer

---

## P0.1: Enhanced Source of Truth Enforcement

### 📋 Task List

#### Day 1: Analysis & Planning
- [ ] Review current system instructions
- [ ] Identify all price-related responses
- [ ] Document current source hierarchy usage
- [ ] Create validation checklist

#### Day 2: Implementation
- [ ] Enhance system instructions with explicit Level 1 enforcement
- [ ] Create `validate_source_of_truth()` function
- [ ] Add pre-response validation hook
- [ ] Implement source usage logging

#### Day 3: Testing & Documentation
- [ ] Test price responses use Level 1
- [ ] Test conflict detection
- [ ] Document validation process
- [ ] Create runbook for source enforcement

### 📝 Code Template

```python
# source_of_truth_validator.py

def validate_source_of_truth(response_data, knowledge_base_sources):
    """
    Validates that response uses Level 1 (Master) source
    
    Returns:
        dict: Validation result with warnings/errors
    """
    validation_result = {
        "valid": True,
        "source_used": None,
        "warnings": [],
        "errors": []
    }
    
    # Check if price is in response
    if "price" in response_data or "$" in str(response_data):
        # Verify Level 1 source was consulted
        level_1_consulted = check_level_1_consultation(knowledge_base_sources)
        
        if not level_1_consulted:
            validation_result["valid"] = False
            validation_result["errors"].append(
                "Price response must use Level 1 (Master) source"
            )
    
    return validation_result
```

### ✅ Success Criteria
- [ ] 100% of price responses use Level 1 source
- [ ] All source decisions logged
- [ ] Zero instances of invented prices
- [ ] Conflict detection alerts working

---

## P0.2: Comprehensive Test Cases

### 📋 Task List

#### Day 1-2: Formula Documentation
- [ ] Extract all 9 formulas from knowledge base
- [ ] Document each formula with examples
- [ ] Create formula reference document
- [ ] Identify edge cases

#### Day 3-5: Unit Tests
- [ ] Test: Paneles calculation
- [ ] Test: Apoyos calculation
- [ ] Test: Puntos fijación
- [ ] Test: Varilla cantidad
- [ ] Test: Tuercas (metal/hormigón)
- [ ] Test: Tacos hormigón
- [ ] Test: Gotero (frontal/lateral)
- [ ] Test: Remaches
- [ ] Test: Silicona

#### Day 6-7: Integration Tests
- [ ] Test complete quotation flow
- [ ] Test edge cases (zero, negative, very large)
- [ ] Test ROUNDUP rules
- [ ] Create test data fixtures

### 📝 Test Template

```python
# tests/test_quotation_formulas.py

import pytest
from quotation_engine import calculate_paneles, calculate_apoyos

class TestQuotationFormulas:
    
    def test_paneles_calculation_roundup(self):
        """Test that paneles calculation uses ROUNDUP"""
        ancho_total = 10.5
        ancho_util = 1.12
        
        result = calculate_paneles(ancho_total, ancho_util)
        
        # Should round up: 10.5 / 1.12 = 9.375 → 10
        assert result == 10
    
    def test_apoyos_calculation(self):
        """Test apoyos calculation with ROUNDUP"""
        largo = 6.0
        autoportancia = 5.5
        
        result = calculate_apoyos(largo, autoportancia)
        
        # ROUNDUP((6/5.5) + 1) = ROUNDUP(2.09) = 3
        assert result == 3
    
    def test_edge_case_zero_values(self):
        """Test handling of zero values"""
        with pytest.raises(ValueError):
            calculate_paneles(0, 1.12)
    
    def test_edge_case_very_large_numbers(self):
        """Test handling of very large numbers"""
        result = calculate_paneles(10000, 1.12)
        assert result > 0
        assert isinstance(result, int)
```

### ✅ Success Criteria
- [ ] 100% formula coverage
- [ ] All edge cases tested
- [ ] CI/CD integration
- [ ] Zero calculation errors in production

---

## P0.3: Detailed Logging

### 📋 Task List

#### Day 1: Infrastructure Setup
- [ ] Choose logging framework (loguru recommended)
- [ ] Set up structured logging (JSON format)
- [ ] Configure log levels
- [ ] Set up log aggregation (if needed)

#### Day 2: Implementation
- [ ] Add trace IDs to all requests
- [ ] Log source selection decisions
- [ ] Log formula applications
- [ ] Log conflict detections
- [ ] Log guardrail checks

#### Day 3: Log Aggregation
- [ ] Set up log storage
- [ ] Create log search interface
- [ ] Set up log retention policy
- [ ] Create log analysis queries

#### Day 4: Documentation
- [ ] Document logging standards
- [ ] Create debugging guide
- [ ] Document trace ID usage
- [ ] Create log analysis runbook

### 📝 Logging Template

```python
# logging_setup.py

from loguru import logger
import uuid
from contextvars import ContextVar

# Context variable for trace ID
trace_id_var: ContextVar[str] = ContextVar('trace_id', default=None)

def setup_logging():
    """Set up structured logging"""
    logger.add(
        "logs/panelin_{time}.json",
        format="{time} | {level} | {message}",
        serialize=True,  # JSON format
        rotation="100 MB",
        retention="30 days"
    )

def log_source_decision(source_level, source_file, product_id):
    """Log source of truth decision"""
    trace_id = trace_id_var.get()
    logger.info(
        "Source decision made",
        extra={
            "trace_id": trace_id,
            "source_level": source_level,
            "source_file": source_file,
            "product_id": product_id,
            "event_type": "source_decision"
        }
    )

def log_formula_application(formula_name, inputs, output):
    """Log formula application"""
    trace_id = trace_id_var.get()
    logger.info(
        "Formula applied",
        extra={
            "trace_id": trace_id,
            "formula": formula_name,
            "inputs": inputs,
            "output": output,
            "event_type": "formula_application"
        }
    )
```

### ✅ Success Criteria
- [ ] All critical paths logged
- [ ] Trace IDs enable full request tracking
- [ ] Average debugging time reduced by 50%
- [ ] Log search interface functional

---

## P0.4: Conflict Detection & Reporting

### 📋 Task List

#### Day 1: Analysis
- [ ] Analyze knowledge base structure
- [ ] Identify conflict-prone areas (prices, specs)
- [ ] Design conflict detection algorithm
- [ ] Create conflict schema

#### Day 2-3: Implementation
- [ ] Create conflict detection engine
- [ ] Implement price comparison
- [ ] Implement specification comparison
- [ ] Add conflict severity levels

#### Day 4: Reporting
- [ ] Generate conflict reports (JSON)
- [ ] Generate conflict reports (Markdown)
- [ ] Add resolution recommendations
- [ ] Create conflict dashboard

#### Day 5: Integration
- [ ] Integrate with logging system
- [ ] Add conflict alerts
- [ ] Set up conflict monitoring
- [ ] Create conflict resolution workflow

### 📝 Conflict Detection Template

```python
# conflict_detector.py

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Conflict:
    product_id: str
    field: str
    level_1_value: any
    level_2_value: any
    level_3_value: any
    severity: str  # "critical", "warning", "info"
    recommendation: str

class ConflictDetector:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def detect_conflicts(self) -> List[Conflict]:
        """Detect conflicts between knowledge base levels"""
        conflicts = []
        
        # Compare Level 1 vs Level 2
        for product in self.kb.get_all_products():
            level_1_data = self.kb.get_level_1(product.id)
            level_2_data = self.kb.get_level_2(product.id)
            
            if level_1_data and level_2_data:
                price_conflict = self._compare_prices(
                    product.id, level_1_data, level_2_data
                )
                if price_conflict:
                    conflicts.append(price_conflict)
        
        return conflicts
    
    def _compare_prices(self, product_id, level_1, level_2):
        """Compare prices between levels"""
        if level_1.get("price") != level_2.get("price"):
            return Conflict(
                product_id=product_id,
                field="price",
                level_1_value=level_1.get("price"),
                level_2_value=level_2.get("price"),
                level_3_value=None,
                severity="critical",
                recommendation="Use Level 1 price, update Level 2"
            )
        return None
    
    def generate_report(self, conflicts: List[Conflict]) -> Dict:
        """Generate conflict report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_conflicts": len(conflicts),
            "critical": len([c for c in conflicts if c.severity == "critical"]),
            "warnings": len([c for c in conflicts if c.severity == "warning"]),
            "conflicts": [self._conflict_to_dict(c) for c in conflicts]
        }
```

### ✅ Success Criteria
- [ ] All conflicts detected within 24 hours
- [ ] Conflict resolution time reduced by 60%
- [ ] Zero unresolved critical conflicts
- [ ] Conflict dashboard operational

---

## 📊 Daily Standup Template

### Questions for Each Day:
1. What did I complete yesterday?
2. What will I work on today?
3. Are there any blockers?
4. What's the status of my P0 item?

### Week 1 Focus:
- **Monday-Tuesday:** P0.1 and P0.3 setup
- **Wednesday-Thursday:** P0.1 and P0.3 implementation
- **Friday:** P0.1 and P0.3 testing and documentation

### Week 2 Focus:
- **Monday-Tuesday:** P0.2 formula documentation
- **Wednesday-Friday:** P0.2 testing and P0.4 implementation

---

## 🎯 Definition of Done

Each P0 item is considered done when:
- [ ] All tasks completed
- [ ] Code reviewed and approved
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Success criteria met
- [ ] Deployed to staging
- [ ] Validated in staging

---

## 📞 Support & Questions

- **Technical Questions:** Backend Lead
- **Process Questions:** Project Manager
- **Blockers:** Escalate immediately

---

**Ready to start?** Begin with P0.1 Day 1 tasks! 🚀
