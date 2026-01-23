# Troubleshooting Guide

This guide covers common issues and their solutions when working with the Panelin AI System.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [API Key Issues](#api-key-issues)
3. [Knowledge Base Issues](#knowledge-base-issues)
4. [Quotation Issues](#quotation-issues)
5. [GPT Configuration Issues](#gpt-configuration-issues)
6. [Training System Issues](#training-system-issues)
7. [Performance Issues](#performance-issues)
8. [Error Reference](#error-reference)

---

## Installation Issues

### ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'openai'
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Reinstall specific package:**
   ```bash
   pip install openai>=1.0.0
   ```

---

### ImportError with Anthropic/Google

**Symptom:**
```
ImportError: cannot import name 'Anthropic' from 'anthropic'
```

**Solution:**
```bash
# Install optional dependencies
pip install anthropic
pip install google-generativeai
```

---

### Node.js/TypeScript SDK Issues

**Symptom:**
```
Error: Cannot find module '@openai/agents-core'
```

**Solution:**
```bash
# Install Node dependencies
npm install

# Or install specific package
npm install @openai/agents-core openai
```

---

## API Key Issues

### API Key Not Found

**Symptom:**
```
OpenAI API key not found. Set OPENAI_API_KEY environment variable.
```

**Solutions:**

1. **Check .env file exists:**
   ```bash
   cat .env
   ```

2. **Verify key format:**
   ```bash
   # Should start with sk-
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Load environment manually:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. **Set directly (temporary):**
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

---

### Invalid API Key

**Symptom:**
```
openai.AuthenticationError: Invalid API key
```

**Solutions:**

1. **Verify key is valid** at [platform.openai.com](https://platform.openai.com)
2. **Check for extra spaces:**
   ```bash
   # Wrong (has spaces)
   OPENAI_API_KEY= sk-your-key 
   
   # Correct
   OPENAI_API_KEY=sk-your-key
   ```

3. **Regenerate key** if compromised

---

### Rate Limit Exceeded

**Symptom:**
```
openai.RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Wait and retry:**
   ```python
   import time
   
   for attempt in range(3):
       try:
           result = api_call()
           break
       except RateLimitError:
           time.sleep(60)  # Wait 1 minute
   ```

2. **Upgrade API plan** at OpenAI dashboard

3. **Implement exponential backoff**

---

## Knowledge Base Issues

### KB Files Not Found

**Symptom:**
```
FileNotFoundError: BMC_Base_Conocimiento_GPT-2.json not found
```

**Solutions:**

1. **Check file location:**
   ```bash
   ls -la "Files/"
   ```

2. **Verify path in code:**
   ```python
   # Use correct path
   kb_path = "Files/"  # Not "files/" - case sensitive
   ```

3. **Check git status:**
   ```bash
   git status
   git checkout -- "Files/"
   ```

---

### Product Not Found in KB

**Symptom:**
```
Error: Product 'ISODEC 100' not found in knowledge base
```

**Solutions:**

1. **Use correct product name:**
   ```python
   # Wrong
   producto="ISODEC 100"
   
   # Correct
   producto="ISODEC EPS"
   espesor="100"
   ```

2. **Check available products:**
   ```python
   import json
   with open("Files/BMC_Base_Unificada_v4.json") as f:
       kb = json.load(f)
       print(kb.keys())
   ```

---

### Conflict Between KB Levels

**Symptom:**
```
Warning: Price conflict detected - Level 1: $46.07, Level 3: $45.99
```

**Solutions:**

1. **Trust Level 1** (always correct)

2. **Run conflict detection:**
   ```bash
   python -m gpt_kb_config_agent.main validate --kb-path "Files/"
   ```

3. **Update lower levels** to match Level 1

---

## Quotation Issues

### Autoportancia Warning

**Symptom:**
```
Warning: ISODEC 100mm cannot span 6m. Maximum autoportancia: 5.5m
```

**Solutions:**

1. **Use thicker panel:**
   ```python
   # For 6m span, use 150mm (7.5m autoportancia)
   producto="ISODEC EPS"
   espesor="150"
   ```

2. **Add intermediate support:**
   - Reduce effective span to < autoportancia

3. **Use PIR instead of EPS** (better for larger spans)

---

### Incorrect Price Calculation

**Symptom:**
Prices don't match expected values

**Solutions:**

1. **Verify KB is loaded correctly:**
   ```python
   from motor_cotizacion_panelin import MotorCotizacionPanelin
   
   motor = MotorCotizacionPanelin()
   print(motor.kb_data)  # Check loaded data
   ```

2. **Check IVA is applied:**
   ```python
   # IVA should be 22%
   total = subtotal * 1.22
   ```

3. **Verify formulas in KB:**
   ```json
   {
     "formulas_cotizacion": {
       "cantidad_paneles": "ceil(area_total / (largo_panel * ancho_util))"
     }
   }
   ```

---

### Missing Materials in Quote

**Symptom:**
Quote doesn't include all materials

**Solutions:**

1. **Check fixing type:**
   ```python
   # Different materials for different fixing types
   tipo_fijacion="hormigon"  # Includes anchors
   tipo_fijacion="madera"    # Includes screws
   ```

2. **Verify KB has material definitions**

---

## GPT Configuration Issues

### GPT Invents Prices

**Symptom:**
GPT responds with prices not in the knowledge base

**Solutions:**

1. **Reinforce in instructions:**
   ```
   BEFORE giving any price: READ ALWAYS BMC_Base_Conocimiento_GPT-2.json
   NEVER invent prices that are not in the JSON
   ```

2. **Upload KB file FIRST** in GPT Builder

3. **Wait for reindexing** (2-3 minutes after upload)

4. **Test with simple query:**
   ```
   "¿Cuánto cuesta ISODEC 100mm?"
   ```

---

### GPT Doesn't Use Function Calling

**Symptom:**
GPT responds without calling the quotation function

**Solutions:**

1. **Verify tools are configured:**
   ```python
   tools = [
       {"type": "function", "function": get_cotizacion_function_schema()},
       {"type": "code_interpreter"}
   ]
   ```

2. **Add explicit instruction:**
   ```
   ALWAYS use calcular_cotizacion() function for quotations
   ```

---

### Personalization Not Working

**Symptom:**
GPT doesn't ask for name or apply personalization

**Solutions:**

1. **Start new conversation** (not continuation)

2. **Verify personalization in instructions:**
   ```
   Al iniciar, SIEMPRE pregunta el nombre del usuario:
   - **Mauro**: ...
   - **Martin**: ...
   - **Rami**: ...
   ```

3. **Check instruction format** (with bold and bullets)

---

## Training System Issues

### Low Evaluation Scores

**Symptom:**
Relevance, groundedness, or coherence scores < threshold

**Solutions:**

1. **Check KB coverage:**
   ```python
   from kb_training_system import KnowledgeBaseLeakDetector
   
   detector = KnowledgeBaseLeakDetector(kb_path="Files/")
   leaks = detector.detect_leaks_batch(interactions)
   ```

2. **Run Level 1 training** with new data

3. **Review and fix identified gaps**

---

### Training Pipeline Fails

**Symptom:**
```
Error during Level 2 training: ...
```

**Solutions:**

1. **Check data format:**
   ```python
   # Interactions should be:
   {
       "query": str,
       "response": str,
       "sources": List[str]
   }
   ```

2. **Run levels individually:**
   ```python
   orchestrator.run_pipeline(levels=[1])  # Test Level 1 only
   ```

3. **Check file permissions**

---

## Performance Issues

### Slow Response Times

**Symptom:**
Quotations take > 10 seconds

**Solutions:**

1. **Use Motor Python directly** (no API call):
   ```python
   from motor_cotizacion_panelin import MotorCotizacionPanelin
   
   motor = MotorCotizacionPanelin()
   result = motor.calcular_cotizacion(...)  # Direct, fast
   ```

2. **Cache KB data:**
   ```python
   # Load KB once, reuse
   motor = MotorCotizacionPanelin()  # Cache instance
   ```

3. **Use appropriate model** (GPT-4 Turbo is faster)

---

### High API Costs

**Symptom:**
API usage costs higher than expected

**Solutions:**

1. **Use Python motor for simple queries**

2. **Implement caching:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_quotation(producto, espesor, area):
       return calcular_cotizacion_agente(...)
   ```

3. **Use cheaper models for non-critical tasks**

---

## Error Reference

### Common Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | `pip install <package>` |
| `FileNotFoundError` | KB file missing | Check path, git checkout |
| `KeyError: 'product'` | Wrong product name | Use correct enum value |
| `AuthenticationError` | Invalid API key | Check .env, regenerate key |
| `RateLimitError` | Too many requests | Wait, implement backoff |
| `JSONDecodeError` | Corrupted KB file | Validate JSON, restore backup |

### Debug Mode

Enable debug mode for detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in .env
PANELIN_DEBUG=true
```

### Getting Help

1. **Check logs:**
   ```bash
   cat panelin.log
   ```

2. **Run diagnostics:**
   ```python
   python verificar_configuracion.py
   ```

3. **Check KB health:**
   ```bash
   python -m gpt_kb_config_agent.main analyze --kb-path "Files/"
   ```

4. **Open an issue** with:
   - Error message
   - Python version
   - Steps to reproduce
   - Environment details

---

## Related Documentation

- [[Getting-Started]] - Initial setup
- [[Configuration]] - Configuration options
- [[API-Reference]] - API documentation

---

<p align="center">
  <a href="[[Configuration]]">← Configuration</a> |
  <a href="[[Home]]">Home →</a>
</p>
