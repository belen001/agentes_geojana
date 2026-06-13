# ADR-13: Estrategia de validación de datos (frontend y backend)

- **Estado:** Propuesto
- **Fecha:** 2026-06-12
- **Ámbito:** **Frontend móvil (PWA ciudadana)** + servicios de dominio. La mecánica de validación de formularios descrita aquí (Zod solo + composable) es específica de la PWA ciudadana; ver §3.6 para la plataforma admin.
- **Relacionado con:** ADR-3 (stack), ADR-4 (Identity & Access), ADR-5 (offline), ADR-6 (servicios + contratos OpenAPI), Recomendaciones de Librerías y Frameworks

---

## 1. Contexto

Geojana tiene dos aplicaciones cliente (PWA ciudadana y plataforma admin) construidas con **Vue.js 3 + Vite / Quasar**, un backend de servicios de dominio en **Python + FastAPI**, un **API Gateway** como punto único de entrada, y **Supabase (PostgreSQL/PostGIS) + Supabase Auth + JWT** como base de datos y autenticación.[^adr3][^adr6-gw]

Hoy los formularios del frontend **no tienen validación** (inputs nativos, datos mock). Antes de integrar el backend necesitamos un **estándar único** que responda, sin ambigüedad, a tres preguntas:

1. ¿Qué se valida en el cliente y qué en el servidor?
2. ¿Cómo se evita que "validación duplicada" se interprete como trabajo redundante u opcional?
3. ¿Cómo se implementa de forma consistente y testeable en ambos lados?

## 2. Decisión

Adoptamos una **validación en dos capas con responsabilidades distintas** (defensa en profundidad):

> **La validación del frontend es para la _experiencia de usuario_. La del backend es para la _seguridad y la integridad de los datos_. No es duplicación opcional: cumplen objetivos diferentes. El backend SIEMPRE re-valida; nunca se confía en el cliente.**

El cliente puede ser evadido (DevTools, llamadas directas a la API con curl/Postman), por lo que **el servidor es la única fuente de verdad**. La capa de front existe para dar feedback inmediato y ahorrar viajes de red, no para garantizar nada.

### 2.1. Clasificación: validación de forma vs. de negocio

Toda validación se clasifica en uno de dos tipos, y eso determina dónde vive:

| Tipo | Definición | ¿Dónde se implementa? |
|---|---|---|
| **De forma (sintáctica)** | Se puede comprobar solo con el dato en mano: obligatorio, longitud mín/máx, formato (email, teléfono), coincidencia de contraseñas | **Front (Zod) + Back (Pydantic)** — en ambos |
| **De negocio (semántica)** | Requiere estado que el cliente no posee: credenciales reales, unicidad, permisos, estado del recurso | **Solo Back** — el front solo refleja el error recibido |

Ejemplos canónicos del proyecto:

| Validación | Front (Zod) | Back | Notas |
|---|:---:|:---:|---|
| Campos obligatorios | ✅ | ✅ | Forma — en ambas capas |
| Límite de caracteres | ✅ | ✅ | Forma — en ambas capas |
| Formato de email / teléfono | ✅ | ✅ | Forma — en ambas capas |
| Contraseña: formato (mín. 8, no vacía) | ✅ | ✅ | Forma del campo |
| **Contraseña incorrecta** | ❌ | ✅ | El front no conoce la credencial; recibe `401` (Supabase Auth / Identity & Access)[^adr4] |
| Email ya registrado | ❌ | ✅ | Solo la BD lo sabe; el front recibe `409` |
| Permiso insuficiente (p. ej. `poi:manage`) | ❌ | ✅ | Lo valida el Gateway/servicio; el front recibe `403`[^adr4] |

### 2.2. Contrato compartido como fuente de verdad

El **contrato OpenAPI/Swagger** de cada servicio es la fuente de verdad de la forma de los datos.[^adr6-contract] Como front (TypeScript) y back (Python) son lenguajes distintos, **no comparten el mismo código de esquema**:

- **Backend:** lo implementa con **Pydantic** (modelos de request/response de FastAPI).
- **Frontend:** lo refleja con **Zod**, manteniéndolo en sincronía con el contrato (a mano o generando tipos desde el OpenAPI).

Regla: si la forma del dato cambia, **primero se actualiza el contrato OpenAPI**, y luego Pydantic y Zod se alinean a él.

## 3. Implementación — Frontend (Zod)

### 3.1. Por qué Zod

- Hoy no hay validación → adopción sin coste de migración.
- **Tipos gratis:** `z.infer<typeof schema>` deriva el tipo TypeScript del esquema; no se duplica `interface` + reglas.
- **Reutilizable:** el mismo esquema valida el formulario, el payload que se envía al Gateway y (a futuro) el reporte antes de encolarlo offline.[^adr5]
- **Encaja con la arquitectura por capas** del proyecto (servicios puros → composables → componentes delgados, MVVM).

> El documento de recomendaciones de librerías propone **VeeValidate 4 + Zod** para formularios. Este ADR mantiene **Zod** como esquema, pero **prescinde de VeeValidate** en la PWA ciudadana y lo reemplaza por un composable propio con `safeParse` (ver §3.6 para el alcance por repositorio). Alternativa evaluada para el esquema: Valibot (más liviano); se elige Zod por madurez y ecosistema.

### 3.2. Estructura por capas

```
src/schemas/        # Model: esquemas Zod + tipos inferidos (fuente de verdad en el front)
src/composables/    # ViewModel: estado reactivo + safeParse + errores
src/components/      # View: solo bindean v-model y muestran el error
```

Esto mantiene los componentes "tontos": la lógica de validación vive en el esquema (dominio) y en el composable (adaptación reactiva), no en el `.vue`.

### 3.3. Ejemplo de referencia

**Esquema** (`src/schemas/register.schema.ts`):

```ts
import { z } from 'zod'

export const registerSchema = z
  .object({
    name: z.string().min(2, 'Ingresa tu nombre'),
    email: z.string().email('Correo inválido'),
    phone: z.string().regex(/^\+?56\s?9\s?\d{4}\s?\d{4}$/, 'Celular chileno inválido'),
    password: z.string().min(8, 'Mínimo 8 caracteres'),
    password2: z.string(),
  })
  .refine((d) => d.password === d.password2, {
    message: 'Las contraseñas no coinciden',
    path: ['password2'],
  })

export type RegisterForm = z.infer<typeof registerSchema>
```

**Validación en el composable** (ViewModel):

```ts
const result = registerSchema.safeParse(values)
if (!result.success) {
  // result.error.issues → { path, message }  →  se mapean a cada FormField
}
```

**Componente** (View): solo bindea `v-model` y pinta `errors[campo]`. El `FormField` recibe una prop `error` para mostrar el mensaje.

### 3.4. Relación con Quasar `:rules` (decisión)

Los componentes `QInput` de Quasar traen un sistema propio de validación vía `:rules` (funciones `val => true | 'mensaje'`). Como la PWA usa **inputs nativos** dentro de `FormField`, **no se usan las `:rules` de Quasar**; el composable con Zod cumple ese rol.

Si en el futuro un formulario migra a `QInput`, se adapta el esquema Zod a una `:rule` con un único helper, manteniendo Zod como fuente de verdad:

```ts
const zodRule = (schema: z.ZodTypeAny) => (val: unknown) => {
  const r = schema.safeParse(val)
  return r.success || r.error.issues[0]!.message
}
// <q-input :rules="[zodRule(registerSchema.shape.email)]" />
```

### 3.5. Validación de respuestas (opcional pero recomendado)

Zod también valida lo que se **recibe** del Gateway: parsear la respuesta con un esquema entrega datos ya tipados y confiables, en vez de asumir la forma del payload.

### 3.6. Alcance por repositorio: PWA ciudadana vs. plataforma admin

La mecánica de las secciones 3.1–3.5 (**Zod solo + composable con `safeParse`**, sin librería de formularios) es la decisión de **este repositorio, la PWA ciudadana móvil**. Se justifica por sus formularios simples, su naturaleza mobile-first, su uso de inputs nativos dentro de `FormField` (§3.4) y la reutilización del mismo esquema para validar el reporte offline antes de encolarlo (§8).

La **plataforma institucional / admin** es un **repositorio aparte** con un stack distinto (PrimeVue en lugar de Quasar, formularios de gestión complejos). Para esa app **no rige la mecánica Zod-solo de este ADR**, sino la recomendación del documento de librerías: **VeeValidate 4 + Zod** (`useForm` / `useField`), más adecuada para formularios con arrays dinámicos y validación por campo en tiempo real.

| | **PWA ciudadana (este repo)** | **Plataforma admin (otro repo)** |
|---|---|---|
| Librería de componentes | Quasar (inputs nativos en `FormField`) | PrimeVue |
| Integración del formulario | Composable propio + `safeParse` | VeeValidate 4 (`useForm`/`useField`) |
| Schema / fuente de verdad | **Zod** | **Zod** |
| Alineación con el contrato | OpenAPI → Zod / Pydantic | OpenAPI → Zod / Pydantic |

> **Denominador común (transversal):** Zod como fuente de verdad del esquema, alineado al contrato OpenAPI y reflejado por Pydantic en el backend. **Lo específico de cada app** es *cómo* se conecta Zod al formulario (composable propio en móvil; VeeValidate en admin). La divergencia de este ADR frente al documento de recomendaciones —quitar VeeValidate (§3.1)— aplica **solo a la PWA ciudadana**.

## 4. Implementación — Backend (FastAPI + Pydantic)

### 4.1. Forma → Pydantic

Cada endpoint declara un modelo Pydantic de request; FastAPI lo valida automáticamente y responde `422` ante errores de forma:

```python
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)
```

### 4.2. Negocio → servicios de dominio

Las reglas semánticas (unicidad, credenciales, estado, permisos) se validan **dentro del servicio correspondiente**, no en Pydantic:

- **Credenciales / identidad / permisos:** Identity & Access Service + Supabase Auth.[^adr4]
- **Unicidad / estado del recurso:** el servicio dueño del dato (p. ej. unicidad de email, estado del reporte en Sighting Service).
- **Token, CORS, rate limiting y manejo uniforme de errores:** centralizados en el **API Gateway**.[^adr6-gw]

El frontend **no** implementa estas reglas (coherente con "el frontend no contiene lógica de negocio").[^adr10-front]

## 5. Contrato de errores y su manejo en el front

Mapeo estándar de respuestas a la UI:

| Código | Significado | Tipo | El front… |
|---|---|---|---|
| `400` | Petición malformada | Forma | Error general (no debería ocurrir si Zod validó) |
| `422` | Error de validación de forma | Forma | Mapea cada error al campo correspondiente |
| `401` | No autenticado / credenciales inválidas | Negocio | Mensaje en el formulario de login |
| `403` | Sin permisos | Negocio | Mensaje general / redirección |
| `409` | Conflicto (p. ej. email duplicado) | Negocio | Mapea al campo en conflicto |
| `429` | Rate limit (Gateway) | Infra | Mensaje "intenta más tarde" |

Los mensajes de validación se gestionan con **vue-i18n** (ya presente) para que sean traducibles; no se hardcodean en los componentes.

## 6. Consecuencias

**Positivas**
- Feedback inmediato y mejor UX en el cliente, con menos viajes de red.
- Seguridad e integridad garantizadas en el servidor, independientes del cliente.
- Una sola fuente de verdad por capa (Zod en front, Pydantic en back) alineadas al contrato OpenAPI.
- Tipos derivados del esquema en el front → menos duplicación y menos drift de tipos.

**Negativas / Trade-offs**
- La forma se declara en dos lugares (Zod y Pydantic): hay que mantenerlos sincronizados con el contrato. Mitigación: el OpenAPI como fuente de verdad y, opcionalmente, generación de tipos.
- Capa adicional de abstracción en el front (esquemas + composable). Se asume por la ganancia en testeabilidad y reutilización.

## 7. Cumplimiento (estándar)

| Criterio | Forma de verificación |
|---|---|
| Validación de forma en el front | Cada formulario tiene un esquema Zod en `src/schemas/` y valida antes de enviar |
| El backend re-valida todo | Cada endpoint tiene su modelo Pydantic; las reglas de negocio viven en el servicio |
| Sin lógica de negocio en el cliente | El front no decide unicidad, permisos ni credenciales; solo refleja el error recibido |
| Fuente de verdad única | Cambios de forma se reflejan primero en el contrato OpenAPI y luego en Zod/Pydantic |
| Tipos derivados, no duplicados | Los tipos del formulario se obtienen con `z.infer`, no con `interface` paralela |
| Mensajes traducibles | Los textos de error pasan por vue-i18n, no hardcodeados |
| Mapeo de errores del servidor | El cliente traduce `401/403/409/422` a mensajes por campo o generales |

## 8. Alcance en la entrega actual (MVP)

Como la PWA trabaja hoy con **datos mock y sin backend**, en esta entrega **solo aplica la capa de front (Zod)**: obligatorios, longitudes, formatos y coincidencia de contraseñas. Las validaciones de negocio (contraseña incorrecta, email duplicado, permisos) se cablean **al integrar el API Gateway**, momento en que el front añadirá únicamente el **mapeo de errores** descrito en la sección 5.

A futuro, en el **modo offline** (ADR-5), el mismo esquema Zod valida el reporte **antes de encolarlo** en IndexedDB, evitando persistir datos con forma inválida.[^adr5]

## 9. Referencias (evidencia)

[^adr3]: Stack confirmado (ADR-3): Vue.js 3 + Vite (frontend), Python + FastAPI (servicios), Supabase PostgreSQL/PostGIS, Supabase Auth + JWT. `evidence_id: ev-d0814d1cfeda-0000`.
[^adr6-gw]: API Gateway como punto único de entrada: valida token, centraliza CORS, rate limiting y manejo uniforme de errores (ADR-6). `evidence_id: ev-027cde2bfdb8-0001`.
[^adr6-contract]: Contratos REST documentados mediante OpenAPI/Swagger como contrato entre frontend, gateway y servicios (ADR-6). `evidence_id: ev-027cde2bfdb8-0006`.
[^adr4]: Identity & Access Service gestiona identidad, roles y permisos; los demás servicios no gestionan permisos directamente (ADR-6/ADR-4). `evidence_id: ev-027cde2bfdb8-0005`.
[^adr10-front]: El frontend no contiene lógica de negocio (referido a POI: Leaflet solo renderiza, no decide reglas), principio extendido aquí a la validación de negocio (ADR-10). `evidence_id: ev-87372be56621-0003`.
[^adr5]: Estrategia offline con persistencia local (IndexedDB) para tiles y datos (ADR-9/ADR-5). `evidence_id: ev-13c8338974f5-0001`.
