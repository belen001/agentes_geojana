# ADR-10 Estrategia de integración geoespacial, desacoplamiento de proveedores de mapas y POI

## Situación
Aceptado
* * *
# Contexto
Geojana requiere capacidades geoespaciales para visualizar mapas interactivos, reportes ciudadanos, puntos de interés, ubicación actual del usuario y consultas dentro de un radio definido. Además, debe funcionar parcialmente en zonas rurales o con conectividad limitada.
El planteamiento del proyecto establece que el sistema debe mostrar marcadores distintivos para reportes y puntos de interés dentro de un radio de 2.5 km, además de permitir que el administrador cree, edite o elimine puntos de interés en el mapa. Estos puntos pueden representar centros de rehabilitación, santuarios, veterinarias, zonas de riesgo, áreas protegidas, refugios temporales o ubicaciones institucionales relevantes.
La arquitectura ya definida en ADR-2 y ADR-6 adopta una Arquitectura Basada en Servicios, con separación por dominio, API Gateway como punto de entrada y servicios internos de grano grueso. ADR-6 define específicamente un **Institution Service** encargado de gestionar instituciones, competencias territoriales, puntos de interés y reglas de derivación . Sin embargo, la versión previa de ADR-10 asignaba los POI al **Sighting Service**, generando una inconsistencia de responsabilidades.
Esta decisión se actualiza para resolver dicha inconsistencia y dejar una frontera clara:
*   **Sighting Service** gestiona reportes.
*   **Institution Service** gestiona instituciones, cobertura, derivación y POI.
*   **Map Service** desacopla proveedores externos de mapas y geocodificación.
*   **Leaflet** solo renderiza mapas, reportes y POI en el frontend.
# Decisión
Se decide que la gestión principal de los **Puntos de Interés (POI)** quedará bajo responsabilidad del **Institution Service**, no del Sighting Service.
Un Punto de Interés será entendido como una entidad geoespacial persistente que representa una ubicación relevante para la operación de Geojana. Puede corresponder a:
*   centro de rehabilitación
*   veterinaria
*   refugio temporal
*   santuario
*   zona de riesgo
*   área protegida
*   punto educativo
*   punto de emergencia
*   ubicación institucional
Cada POI deberá contar, como mínimo, con:

| Atributo | Descripción |
| ---| --- |
| Coordenadas | Latitud y longitud persistidas en PostgreSQL/PostGIS. |
| Tipo o categoría | Emergencia, salud animal, educación, conservación, institucional, riesgo, entre otros. |
| Nombre | Nombre visible del punto. |
| Descripción | Información contextual para usuarios, instituciones o administradores. |
| Estado de visibilidad | Visible, oculto, activo o inactivo. |
| Institución asociada | Institución responsable, cuando corresponda. |
| Prioridad visual | Nivel de importancia para renderizado o filtrado. |
| Iconografía | Marcador o símbolo usado en el mapa. |

La distribución final de responsabilidades queda así:

| Componente | Responsabilidad sobre POI |
| ---| --- |
| Frontend / Leaflet | Renderiza los POI en el mapa, pero no decide reglas de negocio ni persistencia. |
| API Gateway | Valida acceso, token y permisos antes de redirigir solicitudes. |
| Institution Service | Crea, edita, oculta, activa, desactiva y consulta POI. También los relaciona con instituciones, cobertura territorial y reglas de derivación. |
| Sighting Service | Gestiona reportes geolocalizados. Puede consultar POI para contexto, pero no los administra. |
| Map Service | Apoya con geocodificación, reverse geocoding, validación de coordenadas y desacoplamiento de proveedores externos. No gobierna ni persiste POI. |
| PostgreSQL + PostGIS / Supabase | Persiste POI y permite consultas espaciales, como búsqueda por radio, distancia e intersección. |
| Analytics Service | Puede usar POI para métricas geográficas, pero no los modifica. |
| Identity & Access Service | Define permisos como `poi:manage`, pero no administra el contenido geográfico del POI. |

La justificación principal es que los POI están más relacionados con la **red institucional y territorial** que con el ciclo de vida de un reporte. Un reporte ciudadano representa un evento: avistamiento, amenaza o emergencia. En cambio, un POI representa una ubicación estable o semiestable que puede servir para derivación, orientación, educación, gestión territorial o apoyo institucional.
Por lo tanto, ubicar los POI en el Institution Service mejora la cohesión, porque agrupa instituciones, cobertura, derivación y ubicaciones relevantes en un mismo servicio. También reduce el acoplamiento, porque el Sighting Service no necesita conocer internamente las reglas territoriales ni la administración de puntos institucionales; solo solicita información al Institution Service cuando la necesita.

El flujo corregido para crear un POI será:
1. El administrador abre la plataforma web.
2. Selecciona una ubicación sobre el mapa.
3. Leaflet obtiene las coordenadas seleccionadas.
4. El frontend envía la solicitud al API Gateway.
5. El API Gateway valida token y permisos.
6. La solicitud se redirige al Institution Service.
7. Institution Service valida permisos administrativos o `poi:manage`.
8. Institution Service guarda el POI en PostgreSQL/PostGIS.
9. El POI queda disponible para futuras consultas geográficas.
10. Las PWAs recuperan y renderizan el POI mediante Leaflet.

El flujo corregido para crear un reporte será:
1. El usuario abre la PWA.
2. El frontend obtiene coordenadas GPS.
3. El usuario completa el formulario de reporte.
4. La PWA envía la solicitud al API Gateway.
5. El API Gateway valida el token y redirige al Sighting Service.
6. Sighting Service registra el reporte.
7. Sighting Service solicita al Institution Service la institución competente.
8. Institution Service puede usar PostGIS y, si requiere validación externa, solicitar apoyo al Map Service.
9. Sighting Service guarda la derivación del reporte.
10. Content Service entrega instrucciones de acción.
11. Analytics Service refleja el reporte en dashboard dentro del tiempo definido.
# Consecuencias

| Aspecto | Trade-off |
| ---| --- |
| Cohesión | Positiva. Los POI quedan junto a instituciones, cobertura territorial y reglas de derivación, que cambian por razones similares. |
| Bajo acoplamiento | Positiva. Sighting Service no necesita conocer cómo se administran instituciones, jurisdicciones o puntos estables del mapa. |
| Mantenibilidad | Positiva. Si cambia la lógica de POI, se modifica Institution Service y no el servicio de reportes. |
| Claridad arquitectónica | Positiva. Se evita que Sighting Service concentre demasiadas responsabilidades. |
| Consistencia con ADR-6 | Positiva. ADR-6 ya define que Institution Service gestiona instituciones, cobertura, POI y derivación. |
| Consistencia con ADR-4 | Positiva. Los permisos como `poi:manage` pueden ser validados por Identity & Access Service y aplicados por API Gateway antes de llegar a Institution Service. |
| Complejidad de integración | Mixta. Sighting Service debe consultar a Institution Service cuando necesite POI o derivación, pero esto mejora la separación de responsabilidades. |
| Rendimiento | Mixta. Algunas consultas pueden requerir coordinación entre servicios, pero se mitiga con PostGIS, consultas controladas y posibles vistas de lectura. |
| Escalabilidad futura | Positiva. Si los POI crecen demasiado, podrían separarse en un POI Service en una iteración futura, sin afectar el dominio de reportes. |

La consecuencia más importante es que Geojana queda con una frontera de dominio más limpia: **reportes en Sighting Service, territorio institucional y POI en Institution Service, proveedores geoespaciales en Map Service**.
# Cumplimiento

| Criterio | Forma de verificación |
| ---| --- |
| Responsabilidad principal de POI | Toda operación de creación, edición, ocultamiento, activación o desactivación de POI debe implementarse en Institution Service. |
| Sighting Service sin administración de POI | Sighting Service no debe contener endpoints de administración de POI. Solo puede consultarlos mediante Institution Service o consultas autorizadas. |
| Map Service sin persistencia de POI | Map Service no debe guardar ni gobernar POI. Solo valida coordenadas, geocodifica o normaliza respuestas externas. |
| Frontend sin lógica de negocio de POI | Leaflet solo debe renderizar POI recibidos desde APIs internas. No debe decidir reglas de visibilidad, derivación o competencia institucional. |
| Permisos | Las operaciones de POI deben exigir permisos como `poi:manage` o rol Administrador. |
| Persistencia espacial | Los POI deben almacenarse con tipos geoespaciales compatibles con PostgreSQL/PostGIS. |
| Consulta por radio | El sistema debe permitir consultar POI cercanos dentro del radio definido de 2.5 km. |
| Derivación institucional | Institution Service debe poder usar POI, cobertura y reglas territoriales para apoyar la derivación de reportes. |
| Documentación de endpoints | Los endpoints de POI deben estar documentados en OpenAPI/Swagger dentro de Institution Service. |
| Pruebas de integración | Se debe probar el flujo completo: crear POI desde administrador, persistirlo, consultarlo y visualizarlo en el mapa. |

# Notas
Autor: [@Belén Bravo Sepúlveda](#user_mention#132268655)
Día de publicación: 26-05-2026
Última actualización: 6-06-2026