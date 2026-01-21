-- ============================================================================
-- CONSULTAS SQL ÚTILES PARA LA BASE DE DATOS DE INGESTION
-- ============================================================================
-- 
-- Usar con: sqlite3 ingestion_database.db < consultas_utiles.sql
-- O abrir con DB Browser for SQLite
-- ============================================================================

-- ============================================================================
-- CONSULTAS GENERALES
-- ============================================================================

-- Ver todos los registros (últimos 100)
SELECT 
    id,
    source,
    platform,
    timestamp,
    substr(user_query, 1, 50) as query_preview,
    CASE WHEN chatbot_response IS NOT NULL THEN 'Sí' ELSE 'No' END as tiene_respuesta
FROM ingestion_table 
ORDER BY timestamp DESC 
LIMIT 100;

-- Contar registros por fuente
SELECT 
    source,
    COUNT(*) as total,
    COUNT(CASE WHEN chatbot_response IS NOT NULL THEN 1 END) as con_respuesta
FROM ingestion_table 
GROUP BY source
ORDER BY total DESC;

-- Contar registros por plataforma
SELECT 
    platform,
    COUNT(*) as total
FROM ingestion_table 
GROUP BY platform
ORDER BY total DESC;

-- Rango de fechas de los datos
SELECT 
    MIN(timestamp) as fecha_minima,
    MAX(timestamp) as fecha_maxima,
    COUNT(*) as total_registros
FROM ingestion_table;

-- ============================================================================
-- ANÁLISIS DE COTIZACIONES
-- ============================================================================

-- Cotizaciones incompletas (completitud < 70%)
SELECT 
    qa.ingestion_id,
    it.user_query,
    json_extract(qa.analysis_result, '$.completeness_score') as completitud,
    json_extract(qa.analysis_result, '$.product_code') as producto,
    json_extract(qa.analysis_result, '$.issues') as issues
FROM quote_analysis qa
JOIN ingestion_table it ON qa.ingestion_id = it.id
WHERE json_extract(qa.analysis_result, '$.completeness_score') < 0.7
ORDER BY completitud ASC
LIMIT 50;

-- Distribución de productos en cotizaciones
SELECT 
    json_extract(qa.analysis_result, '$.product_code') as producto,
    COUNT(*) as cantidad,
    AVG(json_extract(qa.analysis_result, '$.completeness_score')) as completitud_promedio
FROM quote_analysis qa
WHERE json_extract(qa.analysis_result, '$.product_code') IS NOT NULL
GROUP BY producto
ORDER BY cantidad DESC;

-- Cotizaciones con más issues
SELECT 
    qa.ingestion_id,
    it.user_query,
    json_array_length(json_extract(qa.analysis_result, '$.issues')) as num_issues,
    json_extract(qa.analysis_result, '$.issues') as issues
FROM quote_analysis qa
JOIN ingestion_table it ON qa.ingestion_id = it.id
WHERE json_array_length(json_extract(qa.analysis_result, '$.issues')) > 0
ORDER BY num_issues DESC
LIMIT 20;

-- ============================================================================
-- ANÁLISIS DE REDES SOCIALES
-- ============================================================================

-- Consultas que requieren respuesta
SELECT 
    sma.ingestion_id,
    sma.platform,
    it.user_query,
    sma.engagement_score,
    sma.sentiment,
    sma.topics
FROM social_media_analysis sma
JOIN ingestion_table it ON sma.ingestion_id = it.id
WHERE sma.requires_response = 1
ORDER BY sma.engagement_score DESC
LIMIT 50;

-- Distribución de sentimiento por plataforma
SELECT 
    sma.platform,
    sma.sentiment,
    COUNT(*) as cantidad,
    AVG(sma.engagement_score) as engagement_promedio
FROM social_media_analysis sma
GROUP BY sma.platform, sma.sentiment
ORDER BY sma.platform, cantidad DESC;

-- Consultas con mayor engagement
SELECT 
    sma.ingestion_id,
    sma.platform,
    it.user_query,
    sma.engagement_score,
    sma.sentiment
FROM social_media_analysis sma
JOIN ingestion_table it ON sma.ingestion_id = it.id
ORDER BY sma.engagement_score DESC
LIMIT 30;

-- ============================================================================
-- ANÁLISIS DE RESPUESTAS
-- ============================================================================

-- Respuestas con baja relevancia
SELECT 
    ra.ingestion_id,
    it.user_query,
    substr(it.chatbot_response, 1, 100) as respuesta_preview,
    ra.relevance_score,
    ra.accuracy_score,
    ra.completeness_score,
    json_extract(ra.issues_detected, '$') as issues
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE ra.relevance_score < 0.7
ORDER BY ra.relevance_score ASC
LIMIT 30;

-- Respuestas con baja precisión
SELECT 
    ra.ingestion_id,
    it.user_query,
    ra.accuracy_score,
    ra.completeness_score,
    json_extract(ra.issues_detected, '$') as issues
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE ra.accuracy_score < 0.7
ORDER BY ra.accuracy_score ASC
LIMIT 30;

-- Mejores respuestas (alto score en todos los aspectos)
SELECT 
    ra.ingestion_id,
    it.user_query,
    substr(it.chatbot_response, 1, 100) as respuesta_preview,
    ra.relevance_score,
    ra.accuracy_score,
    ra.completeness_score,
    (ra.relevance_score + ra.accuracy_score + ra.completeness_score) / 3 as score_promedio
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE ra.relevance_score >= 0.8 
  AND ra.accuracy_score >= 0.8 
  AND ra.completeness_score >= 0.8
ORDER BY score_promedio DESC
LIMIT 20;

-- Respuestas con issues detectados
SELECT 
    ra.ingestion_id,
    it.user_query,
    json_array_length(json_extract(ra.issues_detected, '$')) as num_issues,
    json_extract(ra.issues_detected, '$') as issues,
    json_extract(ra.recommendations, '$') as recomendaciones
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE json_array_length(json_extract(ra.issues_detected, '$')) > 0
ORDER BY num_issues DESC
LIMIT 30;

-- ============================================================================
-- ESTADÍSTICAS GENERALES
-- ============================================================================

-- Resumen completo
SELECT 
    'Total registros' as metric,
    COUNT(*) as value
FROM ingestion_table
UNION ALL
SELECT 
    'Con respuesta',
    COUNT(*)
FROM ingestion_table
WHERE chatbot_response IS NOT NULL AND chatbot_response != ''
UNION ALL
SELECT 
    'Cotizaciones analizadas',
    COUNT(*)
FROM quote_analysis
UNION ALL
SELECT 
    'Redes sociales analizadas',
    COUNT(*)
FROM social_media_analysis
UNION ALL
SELECT 
    'Respuestas analizadas',
    COUNT(*)
FROM response_analysis;

-- Promedios de scores
SELECT 
    'Relevancia promedio' as metric,
    AVG(relevance_score) as value
FROM response_analysis
UNION ALL
SELECT 
    'Precisión promedio',
    AVG(accuracy_score)
FROM response_analysis
UNION ALL
SELECT 
    'Completitud promedio',
    AVG(completeness_score)
FROM response_analysis
UNION ALL
SELECT 
    'Completitud cotizaciones',
    AVG(json_extract(analysis_result, '$.completeness_score'))
FROM quote_analysis
UNION ALL
SELECT 
    'Engagement promedio',
    AVG(engagement_score)
FROM social_media_analysis;
