# ⚡ Panelin Agents SDK - Quick Start

## 🚀 Setup Rápido (5 minutos)

### 1. Instalar Dependencias

```bash
npm install
```

### 2. Configurar API Key

Crear archivo `.env`:

```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
```

### 3. Ejecutar Ejemplo

```bash
npm run test
# o
ts-node panelin_agents_sdk_example.ts
```

---

## 📝 Uso Básico

```typescript
import { runWorkflow } from "./panelin_agents_sdk";

// Cotización
const resultado = await runWorkflow({
  input_as_text: "Cotiza ISODEC 100mm, 10m x 5m, luz 4m"
});

console.log(resultado.respuesta);
```

---

## 🔧 Próximos Pasos

1. **Implementar Tools**: Conectar con backend Python
   - `calcular_cotizacion` → `motor_cotizacion_panelin.py`
   - `buscar_en_base_conocimiento` → Archivos JSON de KB
   - `evaluar_vendedor` → Sistema de evaluación

2. **Configurar Backend**: Crear API REST o usar child process

3. **Testing**: Ejecutar ejemplos y validar respuestas

---

## 📚 Documentación Completa

Ver `PANELIN_AGENTS_SDK_README.md` para documentación completa.

---

**Listo para usar!** 🎉
