#!/usr/bin/env python3
"""
Mapeo Automático de Roles: Customer vs Agent
=============================================

Este script mapea automáticamente los roles en conversaciones de entrenamiento,
identificando mensajes de cliente (user/customer) y agente (assistant/panelin).

Características:
- Detección automática de roles basada en patrones
- Validación de alternancia user/assistant
- Corrección de roles incorrectos
- Generación de reporte de mapeo
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path


class RoleMapper:
    """Mapeador automático de roles en conversaciones de entrenamiento."""
    
    # Patrones para identificar mensajes de Panelin (assistant)
    PANELIN_PATTERNS = [
        r'^Hola.*soy.*Panelin',
        r'^Soy.*Panelin',
        r'BMC Assistant Pro',
        r'experto técnico',
        r'cotización.*técnica',
        r'ISODEC|ISOROOF|ISOPANEL|ISOWALL',  # Productos BMC
        r'autoportancia',
        r'fórmula.*cotización',
        r'IVA.*22%',
        r'/estado|/checkpoint|/consolidar',  # Comandos SOP
        r'Ledger',
        r'fuente de verdad',
    ]
    
    # Patrones para identificar mensajes de cliente (user)
    CUSTOMER_PATTERNS = [
        r'^Hola',
        r'^Buenos días|Buenas tardes',
        r'necesito.*cotizar',
        r'cuánto.*cuesta',
        r'precio.*de',
        r'quiero.*saber',
        r'pregunta',
        r'consult',
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Inicializa el mapeador de roles.
        
        Args:
            strict_mode: Si True, valida estrictamente la alternancia user/assistant
        """
        self.strict_mode = strict_mode
        self.stats = {
            'total_messages': 0,
            'mapped_user': 0,
            'mapped_assistant': 0,
            'mapped_system': 0,
            'corrected': 0,
            'errors': []
        }
    
    def detect_role_from_content(self, content: str, previous_role: Optional[str] = None) -> str:
        """
        Detecta el rol basado en el contenido del mensaje.
        
        Args:
            content: Contenido del mensaje
            previous_role: Rol del mensaje anterior (para contexto)
            
        Returns:
            'user', 'assistant', o 'system'
        """
        content_lower = content.lower()
        
        # Patrones de Panelin (assistant)
        panelin_score = sum(1 for pattern in self.PANELIN_PATTERNS 
                           if re.search(pattern, content_lower, re.IGNORECASE))
        
        # Patrones de cliente (user)
        customer_score = sum(1 for pattern in self.CUSTOMER_PATTERNS 
                            if re.search(pattern, content_lower, re.IGNORECASE))
        
        # Si hay comandos SOP, es definitivamente assistant
        if re.search(r'/estado|/checkpoint|/consolidar', content):
            return 'assistant'
        
        # Si menciona productos técnicos BMC, probablemente es assistant
        if panelin_score > customer_score and panelin_score > 0:
            return 'assistant'
        
        # Si es pregunta simple o saludo, probablemente es user
        if customer_score > panelin_score and customer_score > 0:
            return 'user'
        
        # Si no hay señales claras, usar alternancia
        if previous_role:
            return 'user' if previous_role == 'assistant' else 'assistant'
        
        # Default: user (asume que la conversación empieza con el cliente)
        return 'user'
    
    def validate_alternation(self, messages: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Valida que los mensajes alternen correctamente entre user y assistant.
        
        Args:
            messages: Lista de mensajes
            
        Returns:
            (es_válido, lista_de_errores)
        """
        errors = []
        previous_role = None
        
        for i, msg in enumerate(messages):
            current_role = msg.get('role')
            
            # Permitir múltiples mensajes system al inicio
            if current_role == 'system':
                continue
            
            # Validar alternancia
            if previous_role and previous_role == current_role:
                errors.append(
                    f"Mensaje {i+1}: Rol '{current_role}' se repite después de '{previous_role}'. "
                    f"Esperado alternancia."
                )
            
            previous_role = current_role
        
        return len(errors) == 0, errors
    
    def map_conversation(self, conversation: Dict) -> Dict:
        """
        Mapea los roles en una conversación completa.
        
        Args:
            conversation: Diccionario con la conversación
            
        Returns:
            Conversación con roles mapeados y corregidos
        """
        messages = conversation.get('messages', [])
        if not messages:
            return conversation
        
        mapped_messages = []
        previous_role = None
        
        for i, msg in enumerate(messages):
            original_role = msg.get('role', '').lower()
            content = msg.get('content', '')
            
            # Detectar rol si no está definido o está mal
            if not original_role or original_role not in ['user', 'assistant', 'system']:
                detected_role = self.detect_role_from_content(content, previous_role)
                if original_role != detected_role:
                    self.stats['corrected'] += 1
                msg['role'] = detected_role
            else:
                # Validar rol existente
                detected_role = self.detect_role_from_content(content, previous_role)
                if original_role != detected_role and self.strict_mode:
                    # Si hay conflicto, usar el detectado (más confiable)
                    self.stats['corrected'] += 1
                    msg['role'] = detected_role
                    self.stats['errors'].append(
                        f"Conversación {conversation.get('id', 'unknown')}, "
                        f"mensaje {i+1}: Rol corregido de '{original_role}' a '{detected_role}'"
                    )
            
            # Actualizar estadísticas
            role = msg['role']
            self.stats['total_messages'] += 1
            if role == 'user':
                self.stats['mapped_user'] += 1
            elif role == 'assistant':
                self.stats['mapped_assistant'] += 1
            elif role == 'system':
                self.stats['mapped_system'] += 1
            
            # Agregar metadata de mapeo
            if 'metadata' not in msg:
                msg['metadata'] = {}
            msg['metadata']['role_mapped_at'] = datetime.now().isoformat()
            msg['metadata']['role_detection_confidence'] = self._calculate_confidence(content, role)
            
            mapped_messages.append(msg)
            previous_role = role
        
        conversation['messages'] = mapped_messages
        
        # Validar alternancia
        is_valid, errors = self.validate_alternation(mapped_messages)
        if not is_valid:
            conversation['_role_mapping_warnings'] = errors
        
        return conversation
    
    def _calculate_confidence(self, content: str, role: str) -> float:
        """
        Calcula la confianza del mapeo de rol basado en patrones encontrados.
        
        Returns:
            Score de confianza (0.0 - 1.0)
        """
        content_lower = content.lower()
        score = 0.5  # Base
        
        if role == 'assistant':
            matches = sum(1 for pattern in self.PANELIN_PATTERNS 
                         if re.search(pattern, content_lower, re.IGNORECASE))
            score = min(0.5 + (matches * 0.15), 1.0)
        elif role == 'user':
            matches = sum(1 for pattern in self.CUSTOMER_PATTERNS 
                         if re.search(pattern, content_lower, re.IGNORECASE))
            score = min(0.5 + (matches * 0.15), 1.0)
        
        return round(score, 2)
    
    def map_bundle(self, bundle: Dict) -> Dict:
        """
        Mapea roles en todo el bundle de entrenamiento.
        
        Args:
            bundle: Bundle completo de entrenamiento
            
        Returns:
            Bundle con roles mapeados
        """
        conversations = bundle.get('conversations', [])
        
        for conversation in conversations:
            conversation = self.map_conversation(conversation)
        
        # Agregar reporte de mapeo al bundle
        bundle['_role_mapping_report'] = {
            'mapped_at': datetime.now().isoformat(),
            'stats': self.stats.copy(),
            'summary': {
                'total_conversations': len(conversations),
                'total_messages': self.stats['total_messages'],
                'user_messages': self.stats['mapped_user'],
                'assistant_messages': self.stats['mapped_assistant'],
                'system_messages': self.stats['mapped_system'],
                'corrections_made': self.stats['corrected'],
                'errors_count': len(self.stats['errors'])
            }
        }
        
        return bundle
    
    def get_report(self) -> Dict:
        """Retorna el reporte de mapeo."""
        return {
            'stats': self.stats,
            'summary': {
                'total_messages': self.stats['total_messages'],
                'user_messages': self.stats['mapped_user'],
                'assistant_messages': self.stats['mapped_assistant'],
                'system_messages': self.stats['mapped_system'],
                'corrections_made': self.stats['corrected'],
                'errors': self.stats['errors']
            }
        }


def main():
    """Función principal para ejecutar el mapeador desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Mapea automáticamente roles (user/assistant) en bundles de entrenamiento'
    )
    parser.add_argument('input_file', type=str, help='Archivo JSON de entrada (bundle)')
    parser.add_argument('-o', '--output', type=str, help='Archivo JSON de salida (opcional)')
    parser.add_argument('--strict', action='store_true', help='Modo estricto (valida alternancia)')
    parser.add_argument('--report-only', action='store_true', help='Solo generar reporte, no modificar')
    
    args = parser.parse_args()
    
    # Leer bundle
    with open(args.input_file, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    # Mapear roles
    mapper = RoleMapper(strict_mode=args.strict)
    
    if args.report_only:
        # Solo análisis, no modificar
        for conversation in bundle.get('conversations', []):
            mapper.map_conversation(conversation)
        report = mapper.get_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        # Mapear y guardar
        bundle = mapper.map_bundle(bundle)
        
        output_file = args.output or args.input_file.replace('.json', '_mapped.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Bundle mapeado guardado en: {output_file}")
        print(f"📊 Estadísticas:")
        print(f"   - Total mensajes: {mapper.stats['total_messages']}")
        print(f"   - User: {mapper.stats['mapped_user']}")
        print(f"   - Assistant: {mapper.stats['mapped_assistant']}")
        print(f"   - Correcciones: {mapper.stats['corrected']}")
        if mapper.stats['errors']:
            print(f"   - Errores: {len(mapper.stats['errors'])}")


if __name__ == '__main__':
    main()
