# ADR-1.1 Leaflet + OpenStreetMap

# Situación
Propuesto
# Contexto
Geojana requiere un componente de mapas que permita visualizar reportes geolocalizados, puntos de interés, ubicación actual del usuario, marcadores diferenciados y operación parcial en zonas rurales con conectividad limitada.
El planteamiento del proyecto define que el sistema debe permitir la continuidad de funciones geográficas aun cuando exista pérdida de conexión o fallos en la API principal de mapas. En particular, se exige que el mapa y los puntos de interés se carguen localmente sin error, que la aplicación no falle al reportar sin señal y que se mantenga la visualización de incidentes y puntos de interés dentro de un radio de 2.5 km. Estos requerimientos están directamente relacionados con los atributos de disponibilidad y fiabilidad definidos para Geojana.
Inicialmente, la decisión se formuló como “Leaflet + OpenStreetMap”. Sin embargo, ADR-10 definió una estrategia más precisa de integración geoespacial, separando las responsabilidades entre el frontend, los tile providers, el Map Service, los servicios de dominio y la base de datos espacial. Por lo tanto, esta ADR se actualiza para dejar claro que **Leaflet será la librería de renderizado del mapa**, mientras que **OpenStreetMap será el proveedor inicial de tiles**, sin acoplar la lógica del sistema a dicho proveedor.
Esta decisión también debe mantenerse coherente con ADR-2, donde se adopta una Arquitectura Basada en Servicios para reducir acoplamiento, y con ADR-10, donde se establece que los servicios de dominio no deben consumir directamente proveedores externos como OpenStreetMap, Nominatim, HERE Maps u otros equivalentes. ADR-10 define precisamente una separación entre renderizado, geocodificación y dominio, mediante componentes como Frontend, Tile Providers, Map Service y servicios internos.
# Desición
Se decide utilizar **Leaflet como librería frontend de mapas** y **OpenStreetMap como proveedor inicial de tiles**, manteniendo la arquitectura desacoplada mediante una estrategia de proveedores reemplazables y un Map Service para operaciones geoespaciales externas.
1. La decisión queda definida de la siguiente forma:

| Componente | Responsabilidad |
| ---| --- |
| Leaflet | Renderizar el mapa en el frontend, controlar zoom, desplazamiento, capas visuales y marcadores. |
| OpenStreetMap | Actuar como proveedor inicial de tiles para la capa base del mapa. |
| Tile Providers alternativos | Servir como respaldo ante fallos, lentitud o indisponibilidad del proveedor principal. |
| Service Worker / Cache API | Permitir caché parcial de tiles para operación offline, según ADR-9. |
| Map Service | Centralizar geocodificación, reverse geocoding, validación geográfica y configuración de proveedores. |
| PostgreSQL + PostGIS / Supabase | Persistir reportes, puntos de interés y ejecutar consultas espaciales. |
| Institution Service | Administrar puntos de interés, instituciones, zonas de cobertura y reglas de derivación. |
| Sighting Service | Gestionar reportes geolocalizados y consultar información geoespacial mediante servicios internos. |

La decisión no implica que Geojana dependa exclusivamente de OpenStreetMap. OpenStreetMap será el proveedor inicial por su bajo costo, disponibilidad, comunidad y compatibilidad con Leaflet, pero podrá ser reemplazado o complementado por otros proveedores, como CartoDB, Stamen, HERE Maps u otro servicio equivalente, sin modificar la lógica de negocio.
Leaflet se utilizará únicamente como librería de presentación en el frontend. No almacenará reportes, no gestionará reglas de derivación institucional, no ejecutará lógica de negocio y no realizará consultas espaciales complejas. Las operaciones de dominio quedarán en los servicios internos definidos en ADR-6.
Esta decisión es adecuada porque Geojana necesita una solución liviana, compatible con PWA, de bajo costo y funcional en zonas rurales. Leaflet cumple este propósito al permitir una integración sencilla con mapas, marcadores, capas visuales y caché mediante Service Workers. Además, la separación propuesta en ADR-10 evita que la aplicación quede rígidamente acoplada a un único proveedor externo de mapas.
# Consecuencias

| Aspecto | Trade-off |
| ---| --- |
| Costo | Positivo. Leaflet es open source y OpenStreetMap permite iniciar sin costos de licenciamiento, lo que se alinea con la restricción de bajo presupuesto de Geojana. |
| Rendimiento en PWA | Positivo. Leaflet es liviano y adecuado para dispositivos móviles y conexiones inestables. |
| Disponibilidad rural | Positivo. Puede combinarse con Service Worker, Cache API y precarga de tiles para permitir visualización parcial offline. |
| Desacoplamiento | Positivo. La lógica de negocio no dependerá directamente de OpenStreetMap ni de Nominatim. Los proveedores quedan abstraídos mediante configuración, fallback y Map Service. |
| Mantenibilidad | Positivo. Si se cambia el proveedor de tiles o geocodificación, no debería modificarse la lógica de reportes, instituciones o dashboard. |
| Complejidad inicial | Mixto. Se agrega una separación más clara entre Leaflet, Tile Providers y Map Service, lo que aumenta levemente el diseño inicial, pero reduce riesgos futuros. |
| Dependencia externa | Negativo controlado. El sistema sigue dependiendo de proveedores externos de mapas, pero se mitiga mediante caché, fallback y posibilidad de reemplazo. |
| Cobertura offline | Mixto. No se garantiza un mapa completo sin conexión, sino operación parcial en zonas previamente visitadas o precargadas. |
| Geocodificación | Negativo controlado. Servicios como Nominatim pueden tener límites de uso o latencia, por lo que deben tratarse como reemplazables y no como dependencia directa del dominio. |

La consecuencia principal es que Geojana mantiene una solución simple y económica para mapas, pero con una estructura suficientemente flexible para evolucionar. La aplicación puede comenzar usando Leaflet + OpenStreetMap, sin cerrar la posibilidad de integrar nuevos proveedores o mejorar la estrategia offline en futuras iteraciones.
# Cumplimiento
El cumplimiento de esta decisión se verificará mediante las siguientes métricas y pruebas:

| Criterio | Forma de verificación |
| ---| --- |
| Renderizado del mapa | La PWA debe mostrar correctamente el mapa mediante Leaflet en móvil y escritorio. |
| Proveedor inicial | OpenStreetMap debe estar configurado como proveedor inicial de tiles. |
| Compatibilidad con fallback | Debe existir configuración para incorporar al menos un proveedor alternativo de tiles. |
| Desacoplamiento de dominio | Ningún servicio de dominio debe consumir directamente OpenStreetMap, Nominatim, HERE Maps u otro proveedor externo. |
| Uso correcto de Map Service | Las operaciones de geocodificación, reverse geocoding y validación externa deben pasar por Map Service. |
| POI gestionados correctamente | Los puntos de interés deben ser creados, editados y desactivados desde Institution Service, no desde Sighting Service. |
| Visualización de POI y reportes | Leaflet debe renderizar reportes y puntos de interés obtenidos desde APIs internas. |
| Radio de visualización | Los reportes y puntos de interés cercanos deben mostrarse dentro del radio definido de 2.5 km. |
| Offline parcial | Tras visitar o precargar una zona, el mapa debe poder mostrar tiles cacheados y marcadores locales en modo offline. |
| Tiempo de failover | Al simular fallo del proveedor principal, el cambio al proveedor alternativo debe ocurrir en menos de 3 segundos. |
| Tamaño de bundle | El uso de Leaflet no debe provocar que el bundle inicial de la PWA supere el umbral definido para conexiones 3G/4G. |

# Notas
Autor: Belén Bravo Sepúlveda - [b.bravo02@ufromail.cl](mailto:b.bravo02@ufromail.cl)
Día de publicación: 23-05-2026
Última actualización: 06-06-2026