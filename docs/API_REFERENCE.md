# Panelin API Reference

This document provides an overview of the public APIs available in the Panelin system.

## KB Indexing Agent (`agente_kb_indexing.py`)

The `KBIndexingAgent` is the primary interface for searching and retrieving information from the hierarchical Knowledge Base.

### `search_kb`
Searches the Knowledge Base using hybrid semantic + keyword + structured search.

**Parameters:**
- `query` (str): The search query string.
- `level_priority` (int, optional): Preferred KB level (1-4).
- `search_type` (str): Search strategy ('hybrid', 'keyword', 'semantic', 'structured').
- `max_results` (int): Maximum results to return.

**Returns:** `Dict[str, Any]` containing matches and scores.

### `get_product_info`
Retrieves detailed product information from the Level 1 Master KB.

**Parameters:**
- `product_name` (str): Name of the product.
- `thickness` (str, optional): Specific thickness in mm.

**Returns:** `Dict[str, Any]` with product specifications.

---

## KB Update Optimizer (`kb_update_optimizer.py`)

Handles efficient updates to the Knowledge Base by tracking file changes.

### `upload_file_if_changed`
Uploads a file to OpenAI only if its hash has changed.

**Parameters:**
- `file_path` (Path): Path to the file.
- `force` (bool): Force upload even if unchanged.

**Returns:** `Optional[str]` (OpenAI File ID).

---

## Google Sheets Manager (`panelin_improvements/cost_matrix_tools/gsheets_manager.py`)

Handles bidirectional synchronization with Google Sheets.

### `sync_up`
Pushes local JSON data to a Google Sheet.

### `sync_down`
Pulls data from a Google Sheet and updates local JSON.

---

## Training System (`kb_training_system/training_levels.py`)

Implements the 4-level training pipeline.

### `Level1StaticGrounding`
Converts static documentation and quotes into KB entries.

### `Level2InteractionEvolution`
Uses customer interaction logs to evolve the KB.
