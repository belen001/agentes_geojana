# Guía de Design System

> PWA (Vue.js) para reporte ciudadano de avistamientos y emergencias de fauna silvestre en Chile.  
> Orientada a usuarios en zonas rurales con posible baja conectividad.  
> Análisis visual de 7 pantallas del prototipo **\+ variables reales de Figma** (`primary`) y tipografía oficial **Nunito Sans**.

> **Estado de los valores:** la sección §2.1 usa los **tokens reales** exportados de Figma (colección `primary`). Las dimensiones de componentes y la escala tipográfica siguen marcadas con `~aprox.` por derivarse del prototipo.
* * *

## 1\. Resumen Visual

Geojana proyecta una identidad **naturalista, confiable y cívica**, apoyada en un **verde bosque** de marca, neutros muy claros y fotografía de fauna como protagonista.

*   **Tono / personalidad:** sereno, institucional pero cálido; transmite confianza y pertenencia a una comunidad de conservación. Los acentos cromáticos se reservan para comunicar **severidad y tipo de evento**.
*   **Plataforma objetivo:** móvil first (PWA). Aunque los mockups usan frame iOS (status bar 9:41), el lenguaje de componentes —tarjetas redondeadas, _chips_, FAB central, _bottom sheets_— sigue de cerca **Material Design 3 (Material You)**, recomendado como sistema de referencia base.
*   **Densidad:** media-baja; mucho aire, esquinas generosas y sombras suaves. Pensado para toque cómodo y lectura rápida en exteriores.
*   **Código de color por tipo de evento**, replicado en mapa, listas, badges y fichas:
    *   🟢 Verde marca/éxito → Avistamiento (animal sano)
    *   🟠 Naranja (`warning`) → Amenaza (peligro potencial)
    *   🔴 Rojo/rosa (`error`) → Emergencia (animal herido / crítico)
    *   🟣 Morado (`poi`) → Punto de Interés (rehabilitación, santuarios)
    *   🔵 Azul (`blue`) → Información / contactos institucionales
* * *

## 2\. Tokens de Diseño

Nomenclatura **idéntica a la colección de Figma** (`color/categoria/step`). Las rampas usan pasos numéricos donde **mayor número = más oscuro**.

### 2.1 Paleta de colores (valores reales de Figma)

#### `color/brand` — Verde de marca (primario)

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/brand/100` | `#9CBEA1` | Fondos/containers muy suaves, estados hover claros |
| `color/brand/200` | `#75A47C` | Tints suaves, ilustración |
| `color/brand/300` | `#619769` | Acentos secundarios |
| `color/brand/400` | `#4E8A57` | Hover de CTA |
| `color/brand/500` | `#3A7D44` | CTA principal, FAB activo, títulos de acento, iconos de marca |
| `color/brand/600` | `#34703D` | Estado pressed, gradiente de tarjeta-feature |
| `color/brand/700` | `#2E6436` | Gradiente oscuro, controles de mapa |
| `color/brand/800` | `#295730` | Texto verde sobre fondos claros |
| `color/brand/900` | `#234B29` | Verde más oscuro / encabezados sobre foto |

#### `color/brown` — Marrón para Detalles (Terciario)

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/brown/100` | `#8E7562` | Fondos/containers muy suaves, estados hover claros, detalles pequeños |
| `color/brown/200` | `#5E3A1E` | Base: títulos de sección |
| `color/brown/300` | `#422915` | Acentos secundarios |

#### `color/success` — Verde de éxito / Avistamiento _(rampa distinta, más saturada)_

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/success/100` | `#9FCF95` | Fondo de chip/badge de éxito |
| `color/success/200` | `#66B355` | Realce suave |
| `color/success/300` | `#40A02B` | Base de éxito: confirmación, marcador/badge "Avistamiento", estado "Enviado" |
| `color/success/400` | `#338022` | Texto de éxito sobre claro |
| `color/success/500` | `#26601A` | Éxito oscuro |

#### `color/warning` — Naranja / Amenaza

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/warning/100` | `#FFC19D` | Fondo de badge/container de amenaza |
| `color/warning/200` | `#FE9354` | Realce |
| `color/warning/300` | `#FE640B` | Base: marcador/badge "AMENAZA / Especie Invasora", iconos de alerta |
| `color/warning/400` | `#CB5009` | Texto naranja sobre claro (mejor contraste) |
| `color/warning/500` | `#983C07` | Naranja oscuro |

#### `color/error` — Rojo / Emergencia

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/error/100` | `#E46F88` | Fondo de container de error |
| `color/error/200` | `#DB3F61` | Realce |
| `color/error/300` | `#D20F39` | Base: badge "EMERGENCIA", marcador rojo, eventos críticos |
| `color/error/400` | `#A80C2E` | Texto de error sobre claro |
| `color/error/500` | `#7E0922` | Error oscuro |

#### `color/poi` — Morado / Punto de Interés

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/poi/100` | `#B888F5` | Fondo de badge "P. INTERÉS" |
| `color/poi/200` | `#A061F2` | Realce |
| `color/poi/300` | `#8839EF` | Base: marcadores/badges de Centro de Rehabilitación, Santuario |
| `color/poi/400` | `#6D2EBF` | Texto morado sobre claro |
| `color/poi/500` | `#52228F` | Morado oscuro |

#### `color/blue` — Azul / Información institucional

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/blue/100` | `#80C5F8` | Fondo suave |
| `color/blue/200` | `#018CF1` | Base: iconos de contacto (SAG, Rescate Fauna), enlaces, info |
| `color/blue/300` | `#014679` | Azul oscuro / texto sobre claro |

#### `color/neutral` — Neutros (fondos, texto, bordes)

| Token | Hex | Rol de uso |
| ---| ---| --- |
| `color/neutral/50` | `#F9FAFB` | Fondo general de pantalla y superficie de tarjetas |
| `color/neutral/100` | `#F1F1F1` | Fondo de inputs / filas en reposo (`surface-variant`) |
| `color/neutral/200` | `#E3E3E4` | Bordes sutiles de tarjetas, inputs, chips (`outline`) |
| `color/neutral/300` | `#9E9CA0` | Placeholders, labels overline, texto deshabilitado |
| `color/neutral/400` | `#89878B` | Texto terciario |
| `color/neutral/500` | `#747277` | Texto secundario / metadatos |
| `color/neutral/600` | `#68676B` | Texto secundario fuerte |
| `color/neutral/700` | `#5D5B5F` | — |
| `color/neutral/800` | `#515053` | — |
| `color/neutral/900` | `#3A393B` | Texto principal (títulos y cuerpo) |

> **Nota:** la colección no incluye un token de **blanco puro** ni _aliases_ semánticos (`text/primary`, `surface`, `outline`…). Ver §5 para la capa semántica recomendada.

### 2.2 Tipografía

**Familia única del proyecto:** **`Nunito Sans`** (sans-serif humanista redondeada) para todo Geojana — display, headings, cuerpo, labels y badges. Para la PWA conviene _self-hostear_ los pesos para garantizar render consistente _offline_.

| Token | Tamaño `~aprox.` | Peso | Uso en contexto |
| ---| ---| ---| --- |
| `font/display` | 26–28 px | Bold (700) | Título de onboarding, "¡Reporte enviado!" |
| `font/heading-1` | 22 px | SemiBold (600)/Bold | Encabezado grande de pantalla, nombre de especie |
| `font/heading-2` | 18–20 px | SemiBold (600) | "Hola, Amante de la Naturaleza", título de detalle |
| `font/title-card` | 16 px | SemiBold (600) | Título de tarjeta / ítem de lista |
| `font/section-label` | 14–15 px | SemiBold (600) | Encabezados de sección ("Protocolo de Acción") |
| `font/body` | 14 px | Regular (400) | Texto descriptivo |
| `font/body-sm` | 12–13 px | Regular (400) | Metadatos ("a 2km", subtítulos) |
| `font/label` | 11–12 px | SemiBold (600) | Texto de botones y chips |
| `font/overline` | 10–11 px | Bold (700), MAYÚS., tracking amplio | Labels de campo ("CATEGORÍA"), labels de métricas |
| `font/badge` | 9–10 px | ExtraBold (800), MAYÚS. | Texto de badges ("EMERGENCIA") |
| `font/caption-italic` | 13 px | Regular (400) italic | Nombre científico (Leopardus guigna) |

> Nunito Sans dispone de pesos 400/600/700/800/900, suficientes para toda la escala. Recomendado fijar `font-family-base: "Nunito Sans"` como variable global.

### 2.3 Espaciado y layout

Escala base **4 px** (alineada a Material).

| Token | Valor | Uso típico |
| ---| ---| --- |
| `spacing/xs` | 4 px | Separación icono–texto, padding mínimo |
| `spacing/sm` | 8 px | Gap entre metadatos, padding de chips |
| `spacing/md` | 12 px | Gap entre ítems de lista, padding de inputs |
| `spacing/lg` | 16 px | Margen lateral de pantalla, padding de tarjetas, gap entre tarjetas |
| `spacing/xl` | 24 px | Separación entre secciones |
| `spacing/2xl` | 32 px | Bloques destacados, grupos mayores |

*   **Márgenes laterales:** `~16 px`.
*   **Grid:** columna única apilada; el Perfil usa **grid 2 columnas** (tarjetas de métricas) con gap `~12–16 px`; filtros en fila horizontal de chips con scroll.
*   **Bottom navigation:** alto `~56–64 px`, 5 ranuras (central elevada).
* * *

## 3\. Biblioteca de Componentes

### 3.1 Button
*   **Variantes:** `primary` (fondo `brand/500`, texto blanco), `secondary/outline` (borde `brand/500`, texto verde), `disabled` (verde desaturado / opacidad reducida).
*   **Dimensiones:** alto `~48–52 px`, full-width con margen 16 px, `radius/md (~12 px)`.
*   **Reglas:** un solo primario por vista; en wizards va anclado abajo.

### 3.2 Card
*   **Variantes:** `feature` (gradiente `brand/500→600/700` + icono), `media` (con foto de cabecera), `list-item` (avatar circular + texto + badge + chevron), `metric` (número grande + overline), `sand` (fondo beige editorial — _aún sin token_).
*   **Dimensiones:** `radius/lg (~16 px)`, padding interno `~16 px`.

### 3.3 Badge / Pill de estado
*   **Variantes semánticas:** `EMERGENCIA` (`error/300`), `AMENAZA` (`warning/300`), `AVISTAMIENTO` (`success/300`), `P. INTERÉS` (`poi/300`); texto blanco MAYÚS.
*   **Dimensiones:** alto `~18–20 px`, `radius/full`, padding-h `~8 px`, `font/badge`.
*   **Reglas:** comunica tipo/severidad; nunca decorativo; color + etiqueta siempre juntos (accesibilidad).

### 3.4 Chip / Filtro
*   **Estados:** `selected` (fondo `brand/500`, texto blanco) y `default` (fondo `neutral/50`, borde `neutral/200`, texto `neutral/500`). En mapa, punto de color semántico a la izquierda.
*   **Dimensiones:** alto `~32 px`, `radius/full`, padding-h `~12 px`.

### 3.5 Input / Campo
*   **Variantes:** `search` (pill con lupa, radio alto), `text-field` (label overline + valor, fondo `neutral/100`, `radius/md`), `selectable-option` (icono + título + descripción seleccionable).
*   **Reglas:** el formulario de reporte prioriza **opciones predefinidas** sobre texto libre.

### 3.6 Stepper
*   Botones circulares `~40 px` (`–` / `+`) con borde `neutral/200`; número central en `font/display`.

### 3.7 Bottom Navigation
*   5 ítems: Inicio, Mapa/Guía, **Reportar (FAB central)**, Añadir/Validar, Perfil.
*   **Activo:** FAB central en círculo `brand/500` elevado con icono blanco; resto con realce verde superior. Iconos _outline_ `~24 px`.

### 3.8 Avatar
*   Imagen redonda; en Perfil con **insignia de verificación** `success/300` superpuesta.

### 3.9 Onboarding / Carrusel
*   Imagen full-bleed + bloque inferior (display + descripción + CTA) + dots (activo alargado tipo pill, `brand/500`). 3 pasos; último CTA "¡Comenzar!".

### 3.10 List Section
*   Encabezado `font/section-label` + subgrupos ("Enviados" / "Procesando").

### 3.11 Bottom Sheet (mapa)
*   Panel arrastrable con _grabber_, título + contador ("5 Hallazgos") + lista de marcadores. `radius/lg` superior.

### 3.12 Map Marker
*   Pin circular de color semántico (verde/naranja/rojo/morado) con icono blanco + halo translúcido; usuario en azul. Controles flotantes: zoom `+/–` y recentrar (`brand/700`).
* * *

## 4\. Patrones de UI

1. **Código de color por severidad/tipo** replicado idéntico en marcadores, badges, filtros y fichas — patrón visual central.
2. **Tarjeta-acceso desde el Home:** Guía de Emergencia → Conoce la Fauna → Ver Mapa → Último Reporte.
3. **Flujo de reporte por pasos (wizard):** header "Reportar Emergencia", una pregunta por pantalla, opciones predefinidas, CTA "Continuar" anclado; cierra en **confirmación** (check `success/300` + "Institución Notificada" + guías "¿Qué hacer ahora?").
4. **Lista + Detalle** con badge de tipo y chevron.
5. **Validación comunitaria:** "Validar Información" (primary) vs "Información Falsa o Duplicada" (outline) + reputación del autor.
6. **Patrón pedagógico:** pregunta → protocolo numerado con icono → contactos/amenazas, con iconos circulares tintados por color semántico.
7. **Estado de reporte:** etiquetas "Enviado" / "Procesando".
8. **Navegación:** back por chevron + título; bottom nav persistente; bottom sheets arrastrables; onboarding con dots.
* * *

## 5\. Recomendaciones

**Sobre tu colección de Figma actual**

1. **Añadir una capa semántica de** **_aliases_** sobre las rampas crudas, para no referenciar números sueltos en los componentes. Sugerido:
    *   `color/text/primary → neutral/900` · `text/secondary → neutral/500` · `text/tertiary → neutral/300`
    *   `color/surface → #FFFFFF` (falta token) · `color/background → neutral/50` · `color/outline → neutral/200`
    *   `color/primary → brand/500` · `color/primary-pressed → brand/600` · `color/on-primary → #FFFFFF`
    *   `color/danger → error/300` · `color/alert → warning/300` · `color/success → success/300` · `color/info → blue/200` · `color/poi → poi/300`
2. **Falta un token de blanco puro.** Las superficies/tarjetas se ven blancas en el prototipo, pero el neutro más claro es `neutral/50 #F9FAFB`. Define `color/neutral/0 = #FFFFFF` o un `surface` explícito y decide cuál usar en tarjetas.
3. **`blue`** **solo tiene 3 pasos** (100/200/300) frente a 5 de los demás semánticos. Completa la rampa (400/500) si vas a usar texto azul sobre fondos claros y necesitas contraste AA.
4. **Colores vistos en el prototipo que aún no son tokens:** el beige/arena de la card "Conoce la Fauna de la Zona" y el verde muy tenue del lienzo del mapa. Si se mantienen, conviértelos en variables (`color/sand`, `color/map-canvas`) para no usar hex sueltos en código.
5. **Contraste de badges pequeños:** texto blanco sobre `warning/300 #FE640B` y `success/300 #40A02B` puede quedar al límite de AA en tamaño badge; usa el paso `400` para texto o aumenta el peso.
6. **`brand`** **vs** **`success`****:** ahora son rampas distintas (verde marca apagado vs verde éxito vivo) — buena decisión. Documenta explícitamente que **Avistamiento/confirmación usa** **`success`** y la **marca/CTA usa** **`brand`**, para que no se mezclen.

**Faltantes funcionales (público rural / baja conectividad)**

1. Definir estados de **PWA offline**: _skeleton loaders_, "reporte en cola para enviar", _placeholders_ de imagen y _retry_. No aparecen en el prototipo y son críticos.
2. Documentar **escala de elevación** y **radios** como variables (abajo) para compartirlas entre Figma y código.
* * *

## 6\. Elevación y sombras

| Token | Descripción | Uso |
| ---| ---| --- |
| `elevation/0` | Sin sombra, sobre `background` | Secciones planas |
| `elevation/1` | Suave (`y~2 blur~8, 6–8%`) | Tarjetas, inputs, ítems de lista |
| `elevation/2` | Media (`y~4 blur~16, 10–12%`) | Bottom sheet, nav bar, card destacada |
| `elevation/3` | Pronunciada | FAB, controles de mapa, check de confirmación |

Sistema de **elevación baja y suave**; prioriza separar capas con color/espacio.

## 7\. Bordes y radios

| Token | Valor `~aprox.` | Componente |
| ---| ---| --- |
| `radius/sm` | 8 px | Elementos internos pequeños |
| `radius/md` | 12 px | Botones, text-field, opciones |
| `radius/lg` | 16 px | Tarjetas, bottom sheet (superior) |
| `radius/xl` | 20–24 px | Tarjetas-feature grandes |
| `radius/full` | 999 px | Chips, badges, búsqueda, botones circulares, FAB, avatares |

*   **Bordes:** `1 px` color `neutral/200` en reposo; chips/botones outline usan `brand/500`.

## 8\. Patrones de interacción y feedback

*   **Éxito:** check circular `success/300` + mensaje + acción ("Ver reporte"); estado "Enviado".
*   **Procesando:** etiqueta "Procesando" (añadir spinner/skeleton).
*   **Error/severidad:** badges `error/300` y `warning/300`; sección "Principales Amenazas".
*   **Info institucional:** banda "Institución Notificada" + acentos `blue/200` (SAG, Rescate Fauna).
*   **Validación social:** validar/reportar + confianza del autor.
*   **Navegación:** bottom nav con FAB central, back por chevron, bottom sheets, onboarding con dots.
* * *

## Anexo A — Tokens reales (JSON, formato Design Tokens / Figma)

```json
{
  "color": {
    "brand":   { "100":"#9CBEA1","200":"#75A47C","300":"#619769","400":"#4E8A57","500":"#3A7D44","600":"#34703D","700":"#2E6436","800":"#295730","900":"#234B29" },
    "success": { "100":"#9FCF95","200":"#66B355","300":"#40A02B","400":"#338022","500":"#26601A" },
    "warning": { "100":"#FFC19D","200":"#FE9354","300":"#FE640B","400":"#CB5009","500":"#983C07" },
    "error":   { "100":"#E46F88","200":"#DB3F61","300":"#D20F39","400":"#A80C2E","500":"#7E0922" },
    "poi":     { "100":"#B888F5","200":"#A061F2","300":"#8839EF","400":"#6D2EBF","500":"#52228F" },
    "blue":    { "100":"#80C5F8","200":"#018CF1","300":"#014679" },
    "brown":   { "100":"#8E7562","200":"#5E3A1E","300":"#422915" },
    "neutral": { "50":"#F9FAFB","100":"#F1F1F1","200":"#E3E3E4","300":"#9E9CA0","400":"#89878B","500":"#747277","600":"#68676B","700":"#5D5B5F","800":"#515053","900":"#3A393B" }
  },
  "spacing": { "xs":"4px","sm":"8px","md":"12px","lg":"16px","xl":"24px","2xl":"32px" },
  "radius":  { "sm":"8px","md":"12px","lg":"16px","xl":"24px","full":"999px" },
  "font": {
    "family": "Nunito Sans",
    "display":     { "size":"28px","weight":700 },
    "heading-1":   { "size":"22px","weight":700 },
    "heading-2":   { "size":"19px","weight":600 },
    "title-card":  { "size":"16px","weight":600 },
    "section-label":{ "size":"14px","weight":600 },
    "body":        { "size":"14px","weight":400 },
    "body-sm":     { "size":"12px","weight":400 },
    "label":       { "size":"12px","weight":600 },
    "overline":    { "size":"11px","weight":700,"case":"upper" },
    "badge":       { "size":"10px","weight":800,"case":"upper" }
  }
}
```

## Anexo B — Capa semántica sugerida (alias → para Vue/CSS)

```css
:root {
  /* superficies */
  --color-surface: #FFFFFF;
  --color-background: var(--color-neutral-50);   /* #F9FAFB */
  --color-surface-variant: var(--color-neutral-100);
  --color-outline: var(--color-neutral-200);

  /* texto */
  --color-text-primary: var(--color-neutral-900);
  --color-text-secondary: var(--color-neutral-500);
  --color-text-tertiary: var(--color-neutral-300);

  /* marca y acción */
  --color-primary: var(--color-brand-500);
  --color-primary-pressed: var(--color-brand-600);
  --color-on-primary: #FFFFFF;

  /* semántico de eventos */
  --color-sighting: var(--color-success-300); /* avistamiento / éxito */
  --color-alert:    var(--color-warning-300); /* amenaza */
  --color-danger:   var(--color-error-300);   /* emergencia */
  --color-poi:      var(--color-poi-300);      /* punto de interés */
  --color-info:     var(--color-blue-200);     /* institucional */

/* Marrón editorial (títulos, acentos cálidos) --- */
  --color-brown-100: #8E7562;  /* marrón claro / apagado */
  --color-brown-200: #5E3A1E;  /* base: títulos de sección */
  --color-brown-300: #422915;  /* marrón oscuro */

  --font-family-base: "Nunito Sans", system-ui, sans-serif;
}
```

_Sistema de referencia:_ **_Material Design 3_** _adaptado a la marca Geojana. Colores = tokens reales de la colección_ _`primary`_ _de Figma. Tipografía =_ **_Nunito Sans_**_. Dimensiones de componentes_ _`~aprox.`_ _derivadas del prototipo._