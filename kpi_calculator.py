#!/usr/bin/env python3
"""
Calculador de KPIs Auditables para Training Bundle
==================================================

Calcula KPIs exactos y computables para bundles de entrenamiento de Panelin.
Todos los KPIs son auditables, reproducibles y basados en métricas objetivas.

KPIs incluidos:
- Precisión y Completitud
- Cobertura de Anotaciones
- Calidad de Datos
- Distribución de Roles
- Métricas de Conversación
- Validación de Consistencia
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path


class KPICalculator:
    """Calculador de KPIs auditables para bundles de entrenamiento."""
    
    def __init__(self):
        self.kpis = {}
        self.errors = []
        self.warnings = []
    
    def calculate_all(self, bundle: Dict) -> Dict:
        """
        Calcula todos los KPIs del bundle.
        
        Args:
            bundle: Bundle de entrenamiento
            
        Returns:
            Diccionario con todos los KPIs calculados
        """
        self.kpis = {}
        self.errors = []
        self.warnings = []
        
        # KPIs básicos
        self._calculate_basic_metrics(bundle)
        
        # KPIs de anotaciones
        self._calculate_annotation_metrics(bundle)
        
        # KPIs de calidad
        self._calculate_quality_metrics(bundle)
        
        # KPIs de distribución
        self._calculate_distribution_metrics(bundle)
        
        # KPIs de consistencia
        self._calculate_consistency_metrics(bundle)
        
        # KPIs de entrenamiento
        self._calculate_training_metrics(bundle)
        
        # Resumen ejecutivo
        self._calculate_executive_summary()
        
        return {
            'calculated_at': datetime.now().isoformat(),
            'kpis': self.kpis,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': {
                'total_conversations': len(bundle.get('conversations', [])),
                'schema_version': bundle.get('meta', {}).get('version', 'unknown')
            }
        }
    
    def _calculate_basic_metrics(self, bundle: Dict):
        """Calcula métricas básicas del bundle."""
        conversations = bundle.get('conversations', [])
        
        total_messages = 0
        user_messages = 0
        assistant_messages = 0
        system_messages = 0
        total_chars = 0
        total_words = 0
        
        for conv in conversations:
            messages = conv.get('messages', [])
            total_messages += len(messages)
            
            for msg in messages:
                role = msg.get('role', '').lower()
                content = msg.get('content', '')
                
                if role == 'user':
                    user_messages += 1
                elif role == 'assistant':
                    assistant_messages += 1
                elif role == 'system':
                    system_messages += 1
                
                total_chars += len(content)
                total_words += len(content.split())
        
        self.kpis['basic'] = {
            'total_conversations': len(conversations),
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'system_messages': system_messages,
            'avg_messages_per_conversation': round(total_messages / len(conversations), 2) if conversations else 0,
            'total_characters': total_chars,
            'total_words': total_words,
            'avg_chars_per_message': round(total_chars / total_messages, 2) if total_messages else 0,
            'avg_words_per_message': round(total_words / total_messages, 2) if total_messages else 0,
        }
    
    def _calculate_annotation_metrics(self, bundle: Dict):
        """Calcula métricas de anotaciones (intención, sentimiento, entidades)."""
        conversations = bundle.get('conversations', [])
        
        total_messages = 0
        annotated_messages = 0
        intent_annotated = 0
        sentiment_annotated = 0
        entities_annotated = 0
        
        intent_distribution = Counter()
        sentiment_distribution = Counter()
        entity_types = Counter()
        
        for conv in conversations:
            messages = conv.get('messages', [])
            
            for msg in messages:
                total_messages += 1
                annotations = msg.get('annotations', {})
                
                if annotations:
                    annotated_messages += 1
                    
                    if 'intent' in annotations:
                        intent_annotated += 1
                        intent_distribution[annotations['intent']] += 1
                    
                    if 'sentiment' in annotations:
                        sentiment_annotated += 1
                        sentiment_distribution[annotations['sentiment']] += 1
                    
                    if 'entities' in annotations and annotations['entities']:
                        entities_annotated += 1
                        for entity in annotations['entities']:
                            entity_types[entity.get('type', 'unknown')] += 1
        
        self.kpis['annotations'] = {
            'total_messages': total_messages,
            'annotated_messages': annotated_messages,
            'annotation_coverage': round(annotated_messages / total_messages, 4) if total_messages else 0,
            'intent_annotated': intent_annotated,
            'intent_coverage': round(intent_annotated / total_messages, 4) if total_messages else 0,
            'sentiment_annotated': sentiment_annotated,
            'sentiment_coverage': round(sentiment_annotated / total_messages, 4) if total_messages else 0,
            'entities_annotated': entities_annotated,
            'entities_coverage': round(entities_annotated / total_messages, 4) if total_messages else 0,
            'intent_distribution': dict(intent_distribution),
            'sentiment_distribution': dict(sentiment_distribution),
            'entity_types_distribution': dict(entity_types),
        }
    
    def _calculate_quality_metrics(self, bundle: Dict):
        """Calcula métricas de calidad de datos."""
        conversations = bundle.get('conversations', [])
        
        conversations_with_quality = 0
        total_quality_score = 0
        completeness_scores = []
        accuracy_scores = []
        relevance_scores = []
        
        role_alternation_errors = 0
        empty_messages = 0
        very_short_messages = 0  # < 10 caracteres
        very_long_messages = 0   # > 5000 caracteres
        
        for conv in conversations:
            messages = conv.get('messages', [])
            
            # Validar alternancia de roles
            previous_role = None
            for msg in messages:
                role = msg.get('role', '').lower()
                content = msg.get('content', '')
                
                if not content.strip():
                    empty_messages += 1
                elif len(content) < 10:
                    very_short_messages += 1
                elif len(content) > 5000:
                    very_long_messages += 1
                
                if role in ['user', 'assistant']:
                    if previous_role and previous_role == role:
                        role_alternation_errors += 1
                    previous_role = role
            
            # Quality scores de la conversación
            quality_scores = conv.get('quality_scores', {})
            if quality_scores:
                conversations_with_quality += 1
                if 'completeness' in quality_scores:
                    completeness_scores.append(quality_scores['completeness'])
                if 'accuracy' in quality_scores:
                    accuracy_scores.append(quality_scores['accuracy'])
                if 'relevance' in quality_scores:
                    relevance_scores.append(quality_scores['relevance'])
        
        self.kpis['quality'] = {
            'conversations_with_quality_scores': conversations_with_quality,
            'quality_coverage': round(conversations_with_quality / len(conversations), 4) if conversations else 0,
            'avg_completeness': round(sum(completeness_scores) / len(completeness_scores), 4) if completeness_scores else 0,
            'avg_accuracy': round(sum(accuracy_scores) / len(accuracy_scores), 4) if accuracy_scores else 0,
            'avg_relevance': round(sum(relevance_scores) / len(relevance_scores), 4) if relevance_scores else 0,
            'role_alternation_errors': role_alternation_errors,
            'data_quality_issues': {
                'empty_messages': empty_messages,
                'very_short_messages': very_short_messages,
                'very_long_messages': very_long_messages,
            }
        }
    
    def _calculate_distribution_metrics(self, bundle: Dict):
        """Calcula métricas de distribución (roles, tipos, etc.)."""
        conversations = bundle.get('conversations', [])
        
        conversation_types = Counter()
        outcomes = Counter()
        user_names = Counter()
        quotations_generated = 0
        pdfs_generated = 0
        sop_commands_used = Counter()
        
        for conv in conversations:
            metadata = conv.get('metadata', {})
            
            if 'conversation_type' in metadata:
                conversation_types[metadata['conversation_type']] += 1
            
            if 'outcome' in metadata:
                outcomes[metadata['outcome']] += 1
            
            if 'user_name' in metadata:
                user_names[metadata['user_name']] += 1
            
            if metadata.get('quotation_generated'):
                quotations_generated += 1
            
            if metadata.get('pdf_generated'):
                pdfs_generated += 1
            
            if 'sop_commands_used' in metadata:
                for cmd in metadata['sop_commands_used']:
                    sop_commands_used[cmd] += 1
        
        self.kpis['distribution'] = {
            'conversation_types': dict(conversation_types),
            'outcomes': dict(outcomes),
            'user_names': dict(user_names),
            'quotations_generated': quotations_generated,
            'quotation_rate': round(quotations_generated / len(conversations), 4) if conversations else 0,
            'pdfs_generated': pdfs_generated,
            'pdf_rate': round(pdfs_generated / len(conversations), 4) if conversations else 0,
            'sop_commands_distribution': dict(sop_commands_used),
        }
    
    def _calculate_consistency_metrics(self, bundle: Dict):
        """Calcula métricas de consistencia."""
        conversations = bundle.get('conversations', [])
        
        # Validar que todas las conversaciones tengan ID único
        conversation_ids = [conv.get('id') for conv in conversations]
        unique_ids = set(conversation_ids)
        duplicate_ids = len(conversation_ids) - len(unique_ids)
        
        # Validar formato de IDs
        invalid_ids = 0
        for conv_id in conversation_ids:
            if not conv_id or not isinstance(conv_id, str):
                invalid_ids += 1
            elif not re.match(r'^[A-Z0-9_-]+$', conv_id):
                invalid_ids += 1
        
        # Validar timestamps
        messages_with_timestamp = 0
        messages_without_timestamp = 0
        invalid_timestamps = 0
        
        for conv in conversations:
            for msg in conv.get('messages', []):
                if 'timestamp' in msg:
                    messages_with_timestamp += 1
                    try:
                        datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    except:
                        invalid_timestamps += 1
                else:
                    messages_without_timestamp += 1
        
        self.kpis['consistency'] = {
            'unique_conversation_ids': len(unique_ids),
            'duplicate_conversation_ids': duplicate_ids,
            'invalid_conversation_ids': invalid_ids,
            'messages_with_timestamp': messages_with_timestamp,
            'messages_without_timestamp': messages_without_timestamp,
            'timestamp_coverage': round(messages_with_timestamp / self.kpis['basic']['total_messages'], 4) if self.kpis['basic']['total_messages'] else 0,
            'invalid_timestamps': invalid_timestamps,
        }
    
    def _calculate_training_metrics(self, bundle: Dict):
        """Calcula métricas específicas para entrenamiento."""
        meta = bundle.get('meta', {})
        training_types = meta.get('training_type', [])
        
        conversations = bundle.get('conversations', [])
        
        # Contar conversaciones útiles para cada tipo de entrenamiento
        classification_ready = 0
        generation_ready = 0
        
        for conv in conversations:
            messages = conv.get('messages', [])
            
            # Para clasificación: necesita anotaciones de intención/sentimiento
            has_intent_annotations = any(
                msg.get('annotations', {}).get('intent') 
                for msg in messages
            )
            has_sentiment_annotations = any(
                msg.get('annotations', {}).get('sentiment') 
                for msg in messages
            )
            
            if has_intent_annotations or has_sentiment_annotations:
                classification_ready += 1
            
            # Para generación: necesita mensajes assistant con contenido
            has_assistant_messages = any(
                msg.get('role') == 'assistant' and msg.get('content', '').strip()
                for msg in messages
            )
            
            if has_assistant_messages:
                generation_ready += 1
        
        self.kpis['training'] = {
            'training_types': training_types,
            'classification_ready_conversations': classification_ready,
            'classification_readiness': round(classification_ready / len(conversations), 4) if conversations else 0,
            'generation_ready_conversations': generation_ready,
            'generation_readiness': round(generation_ready / len(conversations), 4) if conversations else 0,
            'both_ready_conversations': min(classification_ready, generation_ready),
        }
    
    def _calculate_executive_summary(self):
        """Calcula resumen ejecutivo de KPIs."""
        basic = self.kpis.get('basic', {})
        annotations = self.kpis.get('annotations', {})
        quality = self.kpis.get('quality', {})
        training = self.kpis.get('training', {})
        
        # Score general (0-100)
        scores = []
        
        # Coverage score (0-30 puntos)
        coverage_score = annotations.get('annotation_coverage', 0) * 30
        scores.append(coverage_score)
        
        # Quality score (0-30 puntos)
        quality_score = (
            quality.get('avg_completeness', 0) * 10 +
            quality.get('avg_accuracy', 0) * 10 +
            quality.get('avg_relevance', 0) * 10
        )
        scores.append(quality_score)
        
        # Training readiness (0-20 puntos)
        training_score = (
            training.get('classification_readiness', 0) * 10 +
            training.get('generation_readiness', 0) * 10
        )
        scores.append(training_score)
        
        # Data quality (0-20 puntos)
        total_issues = (
            quality.get('data_quality_issues', {}).get('empty_messages', 0) +
            quality.get('data_quality_issues', {}).get('very_short_messages', 0) +
            quality.get('role_alternation_errors', 0)
        )
        total_messages = basic.get('total_messages', 1)
        quality_penalty = min((total_issues / total_messages) * 20, 20)
        data_quality_score = max(0, 20 - quality_penalty)
        scores.append(data_quality_score)
        
        overall_score = sum(scores)
        
        # Determinar nivel
        if overall_score >= 80:
            level = 'excellent'
        elif overall_score >= 60:
            level = 'good'
        elif overall_score >= 40:
            level = 'fair'
        else:
            level = 'needs_improvement'
        
        self.kpis['executive_summary'] = {
            'overall_score': round(overall_score, 2),
            'level': level,
            'score_breakdown': {
                'annotation_coverage': round(coverage_score, 2),
                'quality_metrics': round(quality_score, 2),
                'training_readiness': round(training_score, 2),
                'data_quality': round(data_quality_score, 2),
            },
            'key_metrics': {
                'total_conversations': basic.get('total_conversations', 0),
                'total_messages': basic.get('total_messages', 0),
                'annotation_coverage': round(annotations.get('annotation_coverage', 0) * 100, 2),
                'avg_quality_score': round(quality.get('avg_completeness', 0) * 100, 2),
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los KPIs."""
        recommendations = []
        
        annotations = self.kpis.get('annotations', {})
        quality = self.kpis.get('quality', {})
        training = self.kpis.get('training', {})
        consistency = self.kpis.get('consistency', {})
        
        # Recomendaciones de anotaciones
        if annotations.get('annotation_coverage', 0) < 0.5:
            recommendations.append(
                f"⚠️ Cobertura de anotaciones baja ({annotations.get('annotation_coverage', 0)*100:.1f}%). "
                "Agregar anotaciones de intención y sentimiento."
            )
        
        # Recomendaciones de calidad
        if quality.get('role_alternation_errors', 0) > 0:
            recommendations.append(
                f"⚠️ {quality.get('role_alternation_errors', 0)} errores de alternancia de roles. "
                "Revisar mapeo de roles."
            )
        
        # Recomendaciones de entrenamiento
        if 'both' in training.get('training_types', []):
            if training.get('classification_readiness', 0) < 0.7:
                recommendations.append(
                    "⚠️ Baja preparación para clasificación. Agregar más anotaciones de intención/sentimiento."
                )
            if training.get('generation_readiness', 0) < 0.7:
                recommendations.append(
                    "⚠️ Baja preparación para generación. Verificar mensajes de assistant."
                )
        
        # Recomendaciones de consistencia
        if consistency.get('duplicate_conversation_ids', 0) > 0:
            recommendations.append(
                f"⚠️ {consistency.get('duplicate_conversation_ids', 0)} IDs duplicados. "
                "Corregir IDs de conversaciones."
            )
        
        if not recommendations:
            recommendations.append("✅ Bundle en buen estado. Listo para entrenamiento.")
        
        return recommendations


# Importar regex para validación de IDs
import re


def main():
    """Función principal para ejecutar el calculador desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Calcula KPIs auditables para bundles de entrenamiento'
    )
    parser.add_argument('input_file', type=str, help='Archivo JSON del bundle')
    parser.add_argument('-o', '--output', type=str, help='Archivo JSON de salida para KPIs')
    parser.add_argument('--format', choices=['json', 'human'], default='json', help='Formato de salida')
    
    args = parser.parse_args()
    
    # Leer bundle
    with open(args.input_file, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    # Calcular KPIs
    calculator = KPICalculator()
    report = calculator.calculate_all(bundle)
    
    # Guardar o mostrar
    if args.format == 'json':
        output_file = args.output or args.input_file.replace('.json', '_kpis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ KPIs calculados y guardados en: {output_file}")
    else:
        # Formato humano
        exec_summary = report['kpis'].get('executive_summary', {})
        print("\n" + "="*60)
        print("RESUMEN EJECUTIVO - KPIs DE ENTRENAMIENTO")
        print("="*60)
        print(f"\n📊 Score General: {exec_summary.get('overall_score', 0)}/100 ({exec_summary.get('level', 'unknown')})")
        print(f"\n📈 Métricas Clave:")
        key_metrics = exec_summary.get('key_metrics', {})
        for key, value in key_metrics.items():
            print(f"   - {key}: {value}")
        print(f"\n💡 Recomendaciones:")
        for rec in exec_summary.get('recommendations', []):
            print(f"   {rec}")
        print("\n" + "="*60)


if __name__ == '__main__':
    main()
