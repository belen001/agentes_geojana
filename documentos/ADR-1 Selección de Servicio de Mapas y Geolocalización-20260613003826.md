# ADR-1 Selección de Servicio de Mapas y Geolocalización

## **Situación**
Aceptado
## **Contexto**
Se ha evaluado seis alternativas tecnológicas para el componente de mapas de la plataforma: Leaflet + OpenStreetMap, Google Maps, OpenLayers, Here Maps, ArcGIS Online y Flutter + flutter\_map. Cada opción fue analizada según los siguientes criterios derivados del planteamiento del proyecto y los ADR previos:

| Criterio | Fuente |
| ---| --- |
| Costo (bajo presupuesto) | ADR-2, sección 2.2 |
| Funcionamiento offline / Redundancia | Tabla 2.1.5, 2.1.6, táctica 2.2.3 |
| Radio de 2.5 km | RF02 |
| Compatibilidad con Vue.js o Svelte | ADR-3 |
| Marcadores diferenciados por tipo | RF02, RF05 |
| Tamaño de bundle reducido (PWA rural) | Sección 2.1.1, ADR-3 |
| Facilidad de implementación (tiempo limitado) | ADR-2, ADR-3 |

## **Decisión**
**Selección final:** Leaflet + OpenStreetMap
### **Matriz de evaluación comparativa**

| Tecnología | Costo | Offline | Radio 2.5 km | Compatible Vue/Svelte | Bundle size | Complejidad | Cumple requisitos |
| ---| ---| ---| ---| ---| ---| ---| --- |
| Leaflet + OSM | ✅ Gratis | ✅ Sí | ✅ Sí | ✅ Sí | ~40 KB | Baja | ✅ Total |
| Google Maps | ❌ Pago | ❌ No (requiere plan) | ✅ Sí | ✅ Sí | ~150 KB | Media | ❌ Costo |
| OpenLayers | ✅ Gratis | ✅ Sí | ✅ Sí | ⚠️ Parcial | ~200 KB | Alta | ⚠️ Parcial |
| Here Maps | ⚠️ Freemium | ⚠️ Parcial | ✅ Sí | ✅ Sí | ~120 KB | Media | ⚠️ Costo incierto |
| ArcGIS Online | ❌ Alto | ❌ No | ✅ Sí | ❌ No | \>1 MB | Alta | ❌ Múltiples |
| Flutter + flutter\_map | ✅ Gratis | ✅ Sí | ✅ Sí | ❌ No (Flutter) | \>2 MB | Alta | ❌ Stack |

### **Puntuación ponderada (1-5, mayor mejor)**

| Criterio (peso) | Leaflet | Google | OpenLayers | Here | ArcGIS | Flutter |
| ---| ---| ---| ---| ---| ---| --- |
| Costo (25%) | 5 | 1 | 5 | 2 | 1 | 5 |
| Offline/Redundancia (20%) | 5 | 1 | 5 | 2 | 1 | 4 |
| Compatibilidad stack (20%) | 5 | 5 | 3 | 4 | 1 | 1 |
| Bundle size (15%) | 5 | 3 | 2 | 3 | 1 | 1 |
| Facilidad implementación (10%) | 5 | 4 | 3 | 3 | 1 | 2 |
| Precisión/<br>Calidad (10%) | 4 | 5 | 5 | 4 | 5 | 4 |
| Puntuación total | 4.80 | 3.10 | 3.85 | 2.90 | 1.45 | 2.55 |

### **Justificación de la selección**
1. **Costo**: Leaflet + OSM es la única opción con costo cero y sin límites de uso que puedan afectar el escalamiento. Google Maps, Here Maps y ArcGIS tienen costos significativos que violan la restricción presupuestaria.
2. **Requisitos offline**: Solo Leaflet y OpenLayers permiten implementar completamente las tácticas de disponibilidad (reintroducción, redundancia pasiva) sin costo adicional. Google Maps y Here Maps requieren planes empresariales.
3. **Stack tecnológico**: Leaflet se integra perfectamente con Vue.js (vue-leaflet) y Svelte (svelte-leaflet), alineándose con ADR-3. Flutter viola esta decisión fundamental.
4. **Rendimiento en zonas rurales**: El bundle de ~40 KB de Leaflet es el más pequeño, permitiendo cargas rápidas incluso en redes 3G/4G limitadas.
5. **Simplicidad**: Leaflet tiene la curva de aprendizaje más baja, permitiendo cumplir con el tiempo de desarrollo limitado del proyecto.
6. **Cumplimiento de requisitos funcionales**: Leaflet cumple todos los RF de la sección 3.1 y 3.2 (marcadores, radio, geolocalización, fichas interactivas).
## **Consecuencias**

| Aspecto | Impacto |
| ---| --- |
| Positivo (+) | Costo cero, sin riesgos financieros |
| Positivo (+) | Implementación completa de tácticas de disponibilidad (offline, redundancia) |
| Positivo (+) | Bundle pequeño, óptimo para zonas rurales |
| Positivo (+) | Rápido desarrollo y baja curva de aprendizaje |
| Positivo (+) | Comunidad grande y documentación extensa |
| Negativo (-) | La geocodificación (búsqueda por dirección) requiere servicio externo (Nominatim) con límites |
| Negativo (-) | Los tile servers públicos pueden tener latencia variable |
| Negativo (-) | No incluye rutas o navegación (no requerido) |

**Mitigaciones:**
*   Geocodificación: Implementar búsqueda por coordenadas + lista de puntos de interés locales como alternativa a Nominatim.
*   Latencia de tiles: Configurar múltiples tile servers (OSM, CartoDB, Stamen) con failover automático.
*   Si el proyecto escala: Se puede desplegar un tile server propio con contenedor Docker (bajo costo).
## **Cumplimiento**

| Verificación | Métrica |
| ---| --- |
| Bundle del frontend | Módulo de mapas < 100 KB (gzipped) |
| Funcionalidad offline | 95% de tiles disponibles sin conexión tras primera carga |
| Redundancia | Failover a tile server alternativo en < 3 segundos |
| Radio 2.5 km | Cálculo preciso de distancia usando Turf.js |
| Costo | $0 mensuales por infraestructura de mapas |
| Integración | Demostrar que `vue-leaflet` o `svelte-leaflet` funciona correctamente |

## **Notas**
Autor: [@Belén Bravo Sepúlveda](#user_mention#132268655)
Día de publicación: 25-05-2026
Última actualización: 25-05-2026