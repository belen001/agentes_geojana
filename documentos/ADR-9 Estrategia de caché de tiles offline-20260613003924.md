# ADR-9 Estrategia de caché de tiles offline

# Situación
Propuesto
# Contexto
Geojana requiere que la visualización de mapas funcione de manera parcial en zonas rurales o con conectividad limitada. Esta necesidad surge porque los usuarios deben poder consultar su ubicación, visualizar reportes cercanos, ver puntos de interés y emitir reportes geolocalizados aun cuando el acceso a internet sea inestable o inexistente.
La decisión es necesaria porque el sistema depende de tiles de mapas entregados por proveedores externos, como OpenStreetMap u otros tile providers configurados como respaldo. Si estos servicios fallan, tienen alta latencia, alcanzan límites de uso o el usuario pierde conexión, la experiencia del mapa podría degradarse y afectar directamente la función principal de Geojana: reportar y consultar incidentes de fauna silvestre en terreno.
El planteamiento del proyecto establece que la aplicación debe permitir operación offline, persistencia local, resincronización posterior y continuidad de funciones geográficas. En particular, se exige que el mapa y los puntos de interés se carguen localmente sin error y que la app no falle al reportar sin señal . Además, ADR-1.1 define Leaflet + OpenStreetMap como base del mapa, con soporte de caché local y redundancia entre proveedores de tiles . ADR-10 separa responsabilidades entre Frontend, Tile Providers, Map Service y servicios de dominio, por lo que la estrategia de caché no debe acoplar la lógica de negocio a un proveedor específico
# Decisión
Se decide implementar una **estrategia híbrida de caché offline de tiles basada en Service Worker personalizado + Cache API del navegador + precarga controlada de tiles por zona**, dejando **IndexedDB solo para metadatos de control** y descartando inicialmente un **tile server propio**.
La solución seleccionada queda definida así:

| Componente | Responsabilidad |
| ---| --- |
| Service Worker personalizado | Interceptar solicitudes de tiles, decidir si responder desde caché, red o proveedor alternativo. |
| Cache API del navegador | Almacenar los archivos de tiles ya descargados, usando la URL normalizada como clave. |
| Precarga de tiles por zona | Guardar anticipadamente tiles de zonas críticas, como ubicación actual, comunas priorizadas, radio de 2.5 km y sectores con alta recurrencia de reportes. |
| IndexedDB | Guardar metadatos: fecha de descarga, proveedor, zona, nivel de zoom, cantidad de reutilizaciones y política de expiración. |
| Tile providers alternativos | Actuar como respaldo cuando el proveedor principal falle o no responda. |
| Map Service | Mantener la configuración de proveedores, prioridades y zonas precargables, sin servir directamente los tiles en esta etapa. |

La estrategia funcionará con el siguiente flujo:
1. El usuario abre el mapa en la PWA.
2. Leaflet solicita tiles al proveedor configurado.
3. El Service Worker intercepta la solicitud.
4. Si el tile existe en Cache API y es válido, se entrega desde caché.
5. Si no existe, se solicita al proveedor principal.
6. Si el proveedor principal falla o supera el tiempo máximo de respuesta, el Service Worker intenta con un proveedor alternativo.
7. Si se obtiene el tile desde red, se guarda en Cache API y se registra su metadata en IndexedDB.
8. Si no hay red ni tile cacheado, se muestra una capa base degradada o mensaje controlado, sin romper la operación de reportes.
9. Los reportes, puntos de interés y marcadores seguirán cargándose desde datos locales o desde los servicios internos cuando exista conexión.
La caché no cubrirá todo el mapa mundial ni todos los niveles de zoom. Se priorizarán tiles de baja y media resolución para asegurar contexto territorial, especialmente en el radio de operación del usuario y zonas institucionalmente relevantes. Esto evita un consumo excesivo de almacenamiento y mantiene viable el uso en dispositivos móviles.

| Alternativa | Evaluación |
| ---| --- |
| Cache API del navegador | Adecuada para guardar respuestas HTTP de tiles. Es simple, nativa en PWAs y compatible con Service Workers. Por sí sola no basta, porque no permite una política avanzada de zonas, expiración o métricas sin lógica adicional. |
| IndexedDB para tiles | Útil para blobs y datos estructurados, pero menos conveniente para tiles como respuestas HTTP. Se usará para metadatos, no como almacenamiento principal de imágenes de tiles. |
| Service Worker personalizado | Alternativa central seleccionada. Permite interceptar solicitudes, aplicar estrategia cache-first/network-first, manejar fallback y medir reutilización. Es coherente con la PWA definida en ADR-3 y ADR-8 . |
| Tiles precargados por zona | Seleccionada como complemento. Mejora disponibilidad rural, pero debe limitarse por radio, zoom y prioridad territorial para no saturar almacenamiento. |
| Tile server propio | No se adopta inicialmente. Entrega mayor control, pero aumenta costos, mantenimiento, almacenamiento, actualizaciones cartográficas y complejidad operativa. Se deja como alternativa futura si el volumen de uso o las restricciones de proveedores externos lo justifican. |

La opción corregida evita usar IndexedDB como repositorio principal de tiles, porque eso duplicaría responsabilidades que la Cache API resuelve mejor. También evita proponer un tile server propio desde el inicio, ya que contradice la restricción de bajo costo y simplicidad operativa definida en ADR-2 . La solución final combina bajo costo, buena cobertura offline parcial, menor complejidad y coherencia con la arquitectura desacoplada de ADR-10.
# Consecuencias

| Aspecto | Trade-off |
| ---| --- |
| Cobertura offline de mapas | Positiva. Los tiles visitados y los tiles precargados por zona estarán disponibles sin conexión. La cobertura no será total, pero sí suficiente para operación parcial en zonas priorizadas. |
| Tiempo de carga de tiles | Positiva. Los tiles reutilizados desde Cache API cargarán más rápido que los solicitados por red, especialmente en conexiones rurales lentas. |
| Consumo de almacenamiento | Mixta. La caché mejora disponibilidad, pero consume espacio local. Se mitigará con límites por tamaño, expiración y eliminación LRU de tiles menos usados. |
| Tiempo de failover entre tile servers | Positiva. El Service Worker puede detectar fallo o timeout del proveedor principal y solicitar el tile a un proveedor alternativo. |
| Complejidad de implementación | Media. Es más complejo que usar solo Cache API, pero menos complejo que operar un tile server propio. |
| Disponibilidad en zonas rurales | Positiva. La PWA puede seguir mostrando mapa base parcial, reportes y puntos de interés cercanos sin depender completamente de internet. |
| Cantidad de tiles reutilizados desde caché | Positiva. La estrategia permite medir y aumentar la reutilización, reduciendo dependencia de servidores externos. |
| Dependencia de proveedores externos | Disminuye parcialmente. No se elimina la dependencia, pero se reduce mediante caché, precarga y fallback. |
| Actualización cartográfica | Negativa controlada. Algunos tiles podrían quedar desactualizados. Se mitigará con expiración por antigüedad y limpieza periódica. |
| Costo operativo | Positiva. No se requiere infraestructura propia adicional, manteniendo bajo costo. |

La decisión favorece disponibilidad y rendimiento percibido, a cambio de mayor lógica en el frontend y consumo controlado de almacenamiento local. Es una estrategia adecuada para el alcance universitario de Geojana porque aprovecha capacidades nativas de PWA sin incorporar infraestructura pesada.

# Cumplimiento
El cumplimiento de esta decisión se verificará mediante las siguientes métricas y pruebas:

| Criterio | Forma de verificación |
| ---| --- |
| Cobertura offline de mapas | Tras visitar una zona, al menos el 90% de los tiles necesarios para el radio de 2.5 km y zooms definidos deben cargarse en modo avión. |
| Tiempo de carga desde caché | Los tiles almacenados localmente deben mostrarse en menos de 500 ms en condiciones normales del dispositivo. |
| Tiempo de failover | Al simular fallo del proveedor principal, el cambio a proveedor alternativo debe ocurrir en menos de 3 segundos, manteniendo lo definido en ADR-1.1. |
| Consumo de almacenamiento | La caché de tiles no debe superar el límite configurado por la PWA. Se recomienda iniciar con un máximo de 100 a 200 MB, ajustable según pruebas. |
| Reutilización de tiles | Al menos el 70% de los tiles de zonas previamente visitadas deben cargarse desde caché durante una segunda navegación. |
| Disponibilidad rural | En pruebas con red inestable o modo offline, la app no debe crashear y debe permitir visualizar mapa parcial, reportes locales y puntos de interés cacheados. |
| Expiración de tiles | Los tiles antiguos deben invalidarse o renovarse según política definida, por ejemplo cada 7 a 30 días según criticidad de la zona. |
| Desacoplamiento de proveedores | El frontend no debe contener lógica de negocio asociada a proveedores; solo debe usar configuración de proveedores y fallback. |
| Compatibilidad con Leaflet | Leaflet debe poder seguir solicitando tiles mediante URLs estándar, sin modificaciones internas de la librería. |
| Observabilidad mínima | Se debe registrar cantidad de tiles servidos desde caché, tiles solicitados por red, errores de proveedor y activaciones de fallback. |

# Notas
Autor: Belén Bravo Sepúlveda - [b.bravo02@ufromail.cl](mailto:b.bravo02@ufromail.cl)
Día de publicación: 06-06-2026
Última actualización: 06-06-2026