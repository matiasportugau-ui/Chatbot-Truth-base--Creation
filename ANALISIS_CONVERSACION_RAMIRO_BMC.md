# ANALISIS CONVERSACION RAMIRO - BMC (2026-01-24)

## 1) Objetivo
Construir una base de conocimientos a partir de la conversacion, detectar errores
del asistente, explicar causas probables y proponer soluciones y plan de accion.

## 2) Base de conocimientos derivada (KB propuesta)
Fuente: conversacion completa provista por el usuario.

### 2.1 Hechos sobre BMC Uruguay
- BMC Uruguay NO fabrica. Suministra, comercializa y asesora tecnicamente.
- Vende soluciones para obras nuevas y reformas.
- Lineas principales:
  - Techos y cubiertas: Isodec EPS/PIR, Isoroof, chapas convencionales.
  - Paredes y fachadas: Isopanel EPS, Isowall PIR, Isofrig PIR.
- Foco de solucion:
  - Aislacion termica.
  - Rapidez de montaje.
  - Eficiencia estructural.
  - Seguridad contra incendio (PIR como referencia).
- Tipos de obra:
  - Viviendas.
  - Depositos y galpones.
  - Industria.
  - Agro.
  - Ampliaciones y reformas.
- Diferencial comercial:
  - Venta consultiva tecnica.
  - Soluciones optimizadas para confort, ahorro de presupuesto, estructura,
    tiempos de obra y problemas a futuro.

### 2.2 Rol del asistente (Panelin)
- Asistencia tecnica en cotizaciones.
- Soporte al equipo de ventas.
- Entrenamiento y estandarizacion comercial/tecnica.

### 2.3 Limitaciones operativas (debe explicitarse)
- No se debe afirmar que puede transcribir audio si la plataforma no lo permite.
- Si no hay transcripcion disponible, pedir texto o un resumen del audio.

### 2.4 KB en formato estructurado (para integracion)
```
kb_bmc_conversacion = {
  "empresa": {
    "nombre": "BMC Uruguay",
    "fabrica": false,
    "actividad": [
      "suministra materiales",
      "comercializa sistemas constructivos",
      "asesora tecnicamente proyectos"
    ],
    "tipo_obra": [
      "viviendas",
      "depositos y galpones",
      "industria",
      "agro",
      "ampliaciones y reformas"
    ]
  },
  "productos": {
    "techos_cubiertas": [
      "Isodec EPS",
      "Isodec PIR",
      "Isoroof",
      "chapas convencionales"
    ],
    "paredes_fachadas": [
      "Isopanel EPS",
      "Isowall PIR",
      "Isofrig PIR"
    ]
  },
  "diferencial": [
    "soluciones tecnicas optimizadas",
    "confort",
    "ahorro de presupuesto",
    "ahorro de estructura",
    "ahorro de tiempos de obra",
    "menos problemas a futuro"
  ],
  "asistente": {
    "rol": [
      "asistencia tecnica en cotizaciones",
      "soporte a ventas",
      "entrenamiento y estandarizacion"
    ],
    "limitaciones": [
      "no transcribir audio si el sistema no lo permite",
      "pedir transcripcion o resumen al usuario"
    ]
  }
}
```

## 3) Errores detectados en la conversacion

### Error 1: Declarar que BMC fabrica
- Evidencia: el asistente dijo que BMC se dedica a la fabricacion.
- Por que es un error: BMC comercializa y asesora, no fabrica.
- Impacto: distorsiona el posicionamiento y puede generar promesas incorrectas.
- Severidad: Alta.

### Error 2: Contradiccion sobre audio
- Evidencia: primero dijo que no podia transcribir audio y luego ofrecio y
  realizo una transcripcion aproximada.
- Por que es un error: genera desconfianza, parece inventado.
- Impacto: perdida de credibilidad con el equipo comercial.
- Severidad: Alta.

### Error 3: Transcripcion inventada o no verificada
- Evidencia: produjo una transcripcion sin acceso real al audio.
- Por que es un error: es contenido no verificado.
- Impacto: feedback basado en texto incorrecto, decisiones equivocadas.
- Severidad: Alta.

### Error 4: Respuesta de valor diferencial sin validacion
- Evidencia: ante "por que elegir BMC", dio una respuesta que el usuario marco
  como no del todo correcta.
- Por que es un error: no valido con el usuario ni con KB la propuesta de valor.
- Impacto: discurso comercial inconsistente.
- Severidad: Media.

### Error 5: Suposiciones de contexto (audio de WhatsApp)
- Evidencia: asumio el origen del audio sin confirmacion.
- Impacto: detalles no relevantes y posible friccion con el usuario.
- Severidad: Baja.

## 4) Causas probables (root causes)
- KB incompleta o no consultada para datos corporativos basicos
  (fabricacion vs comercializacion).
- Falta de guardrails de capacidad: "no transcribir audio si no hay soporte".
- Exceso de seguridad en respuestas de branding sin validacion.
- Falta de protocolo de aclaracion cuando el usuario pide una accion no posible.

## 5) Soluciones propuestas

### 5.1 Correcciones inmediatas (KB y respuestas)
- Agregar regla explicita: "BMC no fabrica, suministra/comercializa y asesora".
- Crear respuesta estandar para:
  - "A que se dedica BMC Uruguay?"
  - "Cual es tu funcion en la empresa?"
- Definir respuesta tipo ante audio:
  - "En este entorno no puedo transcribir audio. Podes pegar el texto o
    compartir un resumen y lo analizo".

### 5.2 Guardrails y entrenamiento
- Regla de veracidad: no generar transcripciones si no se puede acceder al audio.
- Checklist de consistencia: validar hechos de empresa antes de responder.
- Casos de prueba en entrenamiento: "BMC fabrica? -> No".
- Caso de prueba: "Usuario envia audio -> pedir transcripcion".

### 5.3 Ajustes de estilo comercial
- Evitar sobrepromesas o "claims" no aprobados.
- Preguntar antes de definir diferencial: "Que 2 o 3 diferenciales queres
  que priorice?"

## 6) Plan de accion

### Fase 1 (0-3 dias): Correcciones criticas
1) Actualizar KB con la aclaracion "BMC no fabrica".
2) Crear macro-respuesta para audio no transcribible.
3) Agregar test rapido en simulacion (Q/A).

### Fase 2 (1-2 semanas): Alineacion comercial
1) Definir propuesta de valor oficial (bullet points aprobados).
2) Versionar respuesta "por que elegir BMC" con ejemplos reales.
3) Actualizar entrenamiento de equipo con discurso validado.

### Fase 3 (1 mes): Control de calidad continuo
1) Checklist de validacion previo a respuestas corporativas.
2) Registro de feedback del equipo de ventas y ajustes mensuales.
3) KPI: % de respuestas alineadas con KB (objetivo 95%+).

## 7) Resumen ejecutivo
- El error principal fue describir a BMC como fabricante.
- El segundo error critico fue inventar/transcribir un audio sin acceso real.
- La solucion es doble: KB explicita + guardrails de capacidad y validacion.
- Se recomienda estandarizar el discurso comercial y mantenerlo versionado.
