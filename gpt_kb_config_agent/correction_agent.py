#!/usr/bin/env python3
"""
GPT Correction Agent
====================

Agente especializado en aplicar correcciones a la base de conocimientos del GPT
después de identificar errores o recibir feedback del equipo.

Capacidades:
- Recibe correcciones estructuradas
- Identifica archivos KB afectados
- Aplica correcciones a archivos JSON
- Valida cambios
- Genera reportes de cambios
- Prepara archivos para re-subir al GPT
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import copy
from loguru import logger


class GPTCorrectionAgent:
    """
    Agente para aplicar correcciones a la base de conocimientos del GPT.
    
    Procesa correcciones estructuradas y las aplica a los archivos KB correspondientes,
    manteniendo la integridad de la estructura y validando los cambios.
    """
    
    # Mapeo de tipos de corrección a archivos KB afectados
    CORRECTION_FILE_MAPPING = {
        "institucional": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["institucional", "identidad"]
        },
        "producto": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["products", "catalogo"]
        },
        "precio": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["products"]
        },
        "formula": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["formulas_cotizacion", "formulas_ahorro_energetico"]
        },
        "instrucciones": {
            "files": [
                "docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md",
                "PANELIN_INSTRUCTIONS_FINAL.txt",
                "gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt"
            ],
            "sections": []
        },
        "catalogo": {
            "files": [
                "BMC_Base_Conocimiento_GPT-2.json",
                "catalog/out/shopify_catalog_v1.json"
            ],
            "sections": ["catalogo", "products"]
        },
        "capabilities": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["capabilities"]
        },
        "reglas_negocio": {
            "files": ["BMC_Base_Conocimiento_GPT-2.json"],
            "sections": ["reglas_negocio"]
        }
    }
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        backup_enabled: bool = True
    ):
        """
        Inicializa el agente de correcciones.
        
        Args:
            project_root: Ruta raíz del proyecto. Si es None, usa el directorio actual.
            backup_enabled: Si True, crea backups antes de modificar archivos.
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Asume que estamos en la raíz del proyecto
            self.project_root = Path(__file__).parent.parent
        
        self.backup_enabled = backup_enabled
        self.backup_dir = self.project_root / ".corrections_backup"
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"GPT Correction Agent inicializado")
        logger.info(f"Project Root: {self.project_root}")
        logger.info(f"Backup habilitado: {self.backup_enabled}")
    
    def apply_correction(
        self,
        correction_id: str,
        correction_type: str,
        description: str,
        changes: Dict[str, Any],
        priority: str = "P1",
        affected_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Aplica una corrección a los archivos KB correspondientes.
        
        Args:
            correction_id: ID único de la corrección (ej: "KB-001")
            correction_type: Tipo de corrección (institucional, producto, precio, etc.)
            description: Descripción del problema identificado
            changes: Diccionario con los cambios a aplicar
            priority: Prioridad (P0=Crítico, P1=Alta, P2=Media)
            affected_files: Lista opcional de archivos específicos a modificar
        
        Returns:
            Diccionario con el resultado de la corrección
        """
        logger.info(f"Aplicando corrección {correction_id} - Tipo: {correction_type}")
        
        # Identificar archivos afectados
        if affected_files is None:
            affected_files = self._identify_affected_files(correction_type)
        
        # Crear backup si está habilitado
        backup_info = {}
        if self.backup_enabled:
            backup_info = self._create_backup(affected_files, correction_id)
        
        # Aplicar cambios
        results = {}
        errors = []
        
        for file_path in affected_files:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                logger.warning(f"Archivo no encontrado: {file_path}")
                errors.append(f"Archivo no encontrado: {file_path}")
                continue
            
            try:
                result = self._apply_changes_to_file(
                    full_path,
                    correction_type,
                    changes,
                    correction_id
                )
                results[file_path] = result
                logger.info(f"Cambios aplicados a {file_path}")
            except Exception as e:
                error_msg = f"Error aplicando cambios a {file_path}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                results[file_path] = {"success": False, "error": str(e)}
        
        # Generar reporte
        report = {
            "correction_id": correction_id,
            "correction_type": correction_type,
            "description": description,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "affected_files": affected_files,
            "results": results,
            "errors": errors,
            "backup_info": backup_info,
            "success": len(errors) == 0
        }
        
        # Guardar reporte
        self._save_correction_report(report)
        
        return report
    
    def _identify_affected_files(self, correction_type: str) -> List[str]:
        """
        Identifica los archivos KB afectados según el tipo de corrección.
        
        Args:
            correction_type: Tipo de corrección
        
        Returns:
            Lista de rutas de archivos afectados
        """
        if correction_type not in self.CORRECTION_FILE_MAPPING:
            logger.warning(f"Tipo de corrección desconocido: {correction_type}")
            return []
        
        mapping = self.CORRECTION_FILE_MAPPING[correction_type]
        return mapping["files"]
    
    def _create_backup(
        self,
        files: List[str],
        correction_id: str
    ) -> Dict[str, str]:
        """
        Crea backups de los archivos antes de modificarlos.
        
        Args:
            files: Lista de archivos a respaldar
            correction_id: ID de la corrección para nombrar el backup
        
        Returns:
            Diccionario con información de los backups creados
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = self.backup_dir / f"{correction_id}_{timestamp}"
        backup_folder.mkdir(exist_ok=True)
        
        backup_info = {}
        
        for file_path in files:
            source = self.project_root / file_path
            
            if not source.exists():
                continue
            
            # Crear estructura de directorios en backup
            backup_path = backup_folder / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            import shutil
            shutil.copy2(source, backup_path)
            backup_info[file_path] = str(backup_path)
            logger.info(f"Backup creado: {backup_path}")
        
        return {
            "backup_folder": str(backup_folder),
            "files": backup_info
        }
    
    def _apply_changes_to_file(
        self,
        file_path: Path,
        correction_type: str,
        changes: Dict[str, Any],
        correction_id: str
    ) -> Dict[str, Any]:
        """
        Aplica cambios a un archivo específico.
        
        Args:
            file_path: Ruta al archivo a modificar
            correction_type: Tipo de corrección
            changes: Diccionario con los cambios a aplicar
            correction_id: ID de la corrección
        
        Returns:
            Diccionario con el resultado de la operación
        """
        if file_path.suffix == ".json":
            return self._apply_json_changes(file_path, correction_type, changes, correction_id)
        elif file_path.suffix in [".md", ".txt"]:
            return self._apply_text_changes(file_path, correction_type, changes, correction_id)
        else:
            return {
                "success": False,
                "error": f"Tipo de archivo no soportado: {file_path.suffix}"
            }
    
    def _apply_json_changes(
        self,
        file_path: Path,
        correction_type: str,
        changes: Dict[str, Any],
        correction_id: str
    ) -> Dict[str, Any]:
        """
        Aplica cambios a un archivo JSON.
        
        Args:
            file_path: Ruta al archivo JSON
            correction_type: Tipo de corrección
            changes: Diccionario con los cambios a aplicar
            correction_id: ID de la corrección
        
        Returns:
            Diccionario con el resultado de la operación
        """
        # Cargar archivo JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        applied_changes = []
        
        # Aplicar cambios según el tipo de corrección
        if correction_type == "institucional":
            applied_changes = self._apply_institucional_changes(data, changes)
        elif correction_type == "producto":
            applied_changes = self._apply_product_changes(data, changes)
        elif correction_type == "precio":
            applied_changes = self._apply_price_changes(data, changes)
        elif correction_type == "formula":
            applied_changes = self._apply_formula_changes(data, changes)
        elif correction_type == "catalogo":
            applied_changes = self._apply_catalog_changes(data, changes)
        elif correction_type == "capabilities":
            applied_changes = self._apply_capabilities_changes(data, changes)
        elif correction_type == "reglas_negocio":
            applied_changes = self._apply_business_rules_changes(data, changes)
        else:
            # Cambio genérico: aplicar directamente al JSON
            applied_changes = self._apply_generic_changes(data, changes)
        
        # Actualizar metadata
        if "meta" in data:
            if "version" in data["meta"]:
                # Incrementar versión menor
                version = data["meta"]["version"]
                # Manejar versiones con formato especial (ej: "5.0-Unified")
                if "-" in version:
                    base_version = version.split("-")[0]
                    suffix = "-" + "-".join(version.split("-")[1:])
                    parts = base_version.split(".")
                else:
                    parts = version.split(".")
                    suffix = ""
                
                if len(parts) >= 2:
                    try:
                        minor = int(parts[-1]) + 1
                        data["meta"]["version"] = ".".join(parts[:-1]) + f".{minor}" + suffix
                    except ValueError:
                        # Si no se puede parsear, agregar .1
                        data["meta"]["version"] = f"{version}.1"
                else:
                    data["meta"]["version"] = f"{version}.1"
            
            # Agregar registro de corrección
            if "correcciones" not in data["meta"]:
                data["meta"]["correcciones"] = []
            
            data["meta"]["correcciones"].append({
                "id": correction_id,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": correction_type,
                "cambios": applied_changes
            })
        
        # Guardar archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "changes_applied": applied_changes,
            "file_modified": str(file_path)
        }
    
    def _apply_institucional_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios a la sección institucional."""
        applied = []
        
        if "institucional" not in data:
            data["institucional"] = {}
        
        for key, value in changes.items():
            if key == "descripcion":
                data["institucional"]["descripcion"] = value
                applied.append(f"Actualizada descripción institucional")
            elif key == "diferencial":
                data["institucional"]["diferencial"] = value
                applied.append(f"Actualizado diferencial competitivo")
            elif key == "empresa":
                data["institucional"]["empresa"] = value
                applied.append(f"Actualizado nombre de empresa")
            else:
                data["institucional"][key] = value
                applied.append(f"Actualizado campo institucional: {key}")
        
        # También actualizar identidad si es necesario
        if "identidad" in data and "aclaracion_critica" in changes:
            data["identidad"]["aclaracion_critica"] = changes["aclaracion_critica"]
            applied.append("Actualizada aclaración crítica en identidad")
        
        return applied
    
    def _apply_product_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios a productos."""
        applied = []
        
        if "products" not in data:
            data["products"] = {}
        
        product_id = changes.get("product_id")
        if not product_id:
            raise ValueError("product_id es requerido para cambios de producto")
        
        if product_id not in data["products"]:
            # Crear nuevo producto
            data["products"][product_id] = {}
            applied.append(f"Producto creado: {product_id}")
        
        product = data["products"][product_id]
        
        # Aplicar cambios al producto
        for key, value in changes.items():
            if key == "product_id":
                continue
            elif key == "espesores":
                # Actualizar espesores
                if "espesores" not in product:
                    product["espesores"] = {}
                product["espesores"].update(value)
                applied.append(f"Actualizados espesores para {product_id}")
            elif key == "nuevo_espesor":
                # Agregar nuevo espesor
                espesor_data = changes["nuevo_espesor"]
                espesor_value = espesor_data["valor"]
                if "espesores" not in product:
                    product["espesores"] = {}
                product["espesores"][str(espesor_value)] = espesor_data["datos"]
                applied.append(f"Agregado espesor {espesor_value} a {product_id}")
            else:
                product[key] = value
                applied.append(f"Actualizado campo {key} para {product_id}")
        
        # Actualizar catálogo si es necesario
        if "catalogo" in data and "lineas_mencionadas" in changes:
            if "lineas_mencionadas" not in data["catalogo"]:
                data["catalogo"]["lineas_mencionadas"] = {}
            data["catalogo"]["lineas_mencionadas"].update(changes["lineas_mencionadas"])
            applied.append("Actualizado catálogo de líneas mencionadas")
        
        return applied
    
    def _apply_price_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios de precios."""
        applied = []
        
        product_id = changes.get("product_id")
        espesor = changes.get("espesor")
        nuevo_precio = changes.get("nuevo_precio")
        
        if not all([product_id, espesor, nuevo_precio]):
            raise ValueError("product_id, espesor y nuevo_precio son requeridos")
        
        if "products" not in data or product_id not in data["products"]:
            raise ValueError(f"Producto {product_id} no encontrado")
        
        product = data["products"][product_id]
        
        if "espesores" not in product or str(espesor) not in product["espesores"]:
            raise ValueError(f"Espesor {espesor} no encontrado en {product_id}")
        
        precio_anterior = product["espesores"][str(espesor)].get("precio")
        product["espesores"][str(espesor)]["precio"] = nuevo_precio
        
        applied.append(
            f"Precio actualizado: {product_id} {espesor}mm "
            f"${precio_anterior} → ${nuevo_precio}"
        )
        
        return applied
    
    def _apply_formula_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios a fórmulas."""
        applied = []
        
        formula_type = changes.get("tipo_formula", "cotizacion")
        formula_name = changes.get("nombre_formula")
        nueva_formula = changes.get("nueva_formula")
        
        if not formula_name or not nueva_formula:
            raise ValueError("nombre_formula y nueva_formula son requeridos")
        
        section_key = f"formulas_{formula_type}" if formula_type != "cotizacion" else "formulas_cotizacion"
        
        if section_key not in data:
            data[section_key] = {}
        
        formula_anterior = data[section_key].get(formula_name)
        data[section_key][formula_name] = nueva_formula
        
        applied.append(
            f"Fórmula actualizada: {formula_name} "
            f"({formula_anterior} → {nueva_formula})"
        )
        
        return applied
    
    def _apply_catalog_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios al catálogo."""
        applied = []
        
        if "catalogo" not in data:
            data["catalogo"] = {}
        
        for key, value in changes.items():
            if key == "lineas_mencionadas":
                if "lineas_mencionadas" not in data["catalogo"]:
                    data["catalogo"]["lineas_mencionadas"] = {}
                data["catalogo"]["lineas_mencionadas"].update(value)
                applied.append("Actualizadas líneas mencionadas")
            else:
                data["catalogo"][key] = value
                applied.append(f"Actualizado campo catálogo: {key}")
        
        return applied
    
    def _apply_capabilities_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios a capabilities."""
        applied = []
        
        if "capabilities" not in data:
            data["capabilities"] = {}
        
        for key, value in changes.items():
            data["capabilities"][key] = value
            applied.append(f"Actualizado capability: {key}")
        
        return applied
    
    def _apply_business_rules_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios a reglas de negocio."""
        applied = []
        
        if "reglas_negocio" not in data:
            data["reglas_negocio"] = {}
        
        for key, value in changes.items():
            data["reglas_negocio"][key] = value
            applied.append(f"Actualizada regla de negocio: {key}")
        
        return applied
    
    def _apply_generic_changes(
        self,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> List[str]:
        """Aplica cambios genéricos al JSON."""
        applied = []
        
        def update_nested_dict(d: Dict, changes: Dict, path: str = "") -> List[str]:
            applied_changes = []
            for key, value in changes.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict) and key in d and isinstance(d[key], dict):
                    applied_changes.extend(update_nested_dict(d[key], value, current_path))
                else:
                    d[key] = value
                    applied_changes.append(f"Actualizado {current_path}")
            return applied_changes
        
        applied = update_nested_dict(data, changes)
        return applied
    
    def _apply_text_changes(
        self,
        file_path: Path,
        correction_type: str,  # noqa: ARG002
        changes: Dict[str, Any],
        correction_id: str  # noqa: ARG002
    ) -> Dict[str, Any]:
        """
        Aplica cambios a archivos de texto (MD, TXT).
        
        Args:
            file_path: Ruta al archivo de texto
            correction_type: Tipo de corrección
            changes: Diccionario con los cambios a aplicar
            correction_id: ID de la corrección
        
        Returns:
            Diccionario con el resultado de la operación
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        applied_changes = []
        
        # Aplicar cambios según el tipo
        if "replace" in changes:
            # Reemplazo simple de texto
            for old_text, new_text in changes["replace"].items():
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    applied_changes.append(f"Reemplazado: '{old_text[:50]}...'")
        
        if "insert_after" in changes:
            # Insertar texto después de un patrón
            for pattern, new_text in changes["insert_after"].items():
                if pattern in content:
                    content = content.replace(pattern, pattern + "\n" + new_text)
                    applied_changes.append(f"Insertado texto después de patrón")
        
        if "insert_before" in changes:
            # Insertar texto antes de un patrón
            for pattern, new_text in changes["insert_before"].items():
                if pattern in content:
                    content = content.replace(pattern, new_text + "\n" + pattern)
                    applied_changes.append(f"Insertado texto antes de patrón")
        
        # Guardar archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "changes_applied": applied_changes,
            "file_modified": str(file_path)
        }
    
    def _save_correction_report(self, report: Dict[str, Any]) -> Path:
        """
        Guarda el reporte de corrección en un archivo.
        
        Args:
            report: Diccionario con el reporte de corrección
        
        Returns:
            Ruta al archivo de reporte guardado
        """
        reports_dir = self.project_root / "docs" / "corrections"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"{report['correction_id']}_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Reporte guardado: {report_file}")
        return report_file
    
    def batch_apply_corrections(
        self,
        corrections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aplica múltiples correcciones en lote.
        
        Args:
            corrections: Lista de diccionarios con correcciones a aplicar
        
        Returns:
            Diccionario con resultados de todas las correcciones
        """
        logger.info(f"Aplicando lote de {len(corrections)} correcciones")
        
        results = []
        for correction in corrections:
            result = self.apply_correction(**correction)
            results.append(result)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_corrections": len(corrections),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
        
        # Guardar resumen
        summary_file = self.project_root / "docs" / "corrections" / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Resumen de lote guardado: {summary_file}")
        
        return summary
    
    def validate_changes(self, file_path: Path) -> Dict[str, Any]:
        """
        Valida que los cambios aplicados no rompan la estructura del archivo.
        
        Args:
            file_path: Ruta al archivo a validar
        
        Returns:
            Diccionario con resultados de validación
        """
        if file_path.suffix == ".json":
            return self._validate_json(file_path)
        else:
            return {"valid": True, "message": "Validación no implementada para este tipo de archivo"}
    
    def _validate_json(self, file_path: Path) -> Dict[str, Any]:
        """Valida la estructura de un archivo JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validaciones básicas
            errors = []
            warnings = []
            
            # Verificar estructura requerida para BMC_Base_Conocimiento_GPT-2.json
            if "BMC_Base_Conocimiento_GPT-2.json" in str(file_path):
                required_sections = ["meta", "identidad", "products"]
                for section in required_sections:
                    if section not in data:
                        errors.append(f"Sección requerida faltante: {section}")
                
                # Validar estructura de productos
                if "products" in data:
                    for product_id, product in data["products"].items():
                        if "espesores" in product:
                            for espesor, datos in product["espesores"].items():
                                required_fields = ["precio", "autoportancia"]
                                for field in required_fields:
                                    if field not in datos:
                                        warnings.append(
                                            f"Campo recomendado faltante: {product_id}.espesores.{espesor}.{field}"
                                        )
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "file": str(file_path)
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Error de sintaxis JSON: {str(e)}"],
                "file": str(file_path)
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Error validando archivo: {str(e)}"],
                "file": str(file_path)
            }
