# ADR-6 Definición de servicios

## Situación
**Aceptado**
## Contexto
Geojana requiere definir los servicios backend que permitirán implementar la plataforma de reportes geolocalizados de fauna silvestre, manteniendo una arquitectura comprensible, de bajo costo y adecuada para un equipo de desarrollo universitario.
En ADR-2 se definió una **Arquitectura Basada en Servicios** con partición por dominio. Esta decisión descartó microservicios por su complejidad operativa y descartó un monolito tradicional por el riesgo de mezclar responsabilidades de usuario, institución y administración. También se estableció que las PWAs no deben consumir directamente los servicios internos, sino comunicarse mediante una capa de API o Gateway.
En ADR-3 se definió un stack compuesto por frontend PWA, servicios de dominio con APIs REST, API Gateway, Python para servicios de dominio, Node.js para la capa de API y Supabase/PostgreSQL + PostGIS para persistencia.
El sistema debe cubrir funcionalidades de mapas, reportes, educación, usuarios, gamificación, dashboard y gestión administrativa. Entre sus requerimientos principales se encuentran: reportar incidentes geolocalizados, capturar GPS, derivar reportes a instituciones competentes, gestionar puntos de interés, mantener guías de emergencia, administrar usuarios e instituciones, visualizar dashboard y permitir operación offline parcial.
Por lo tanto, la definición de servicios debe equilibrar dos fuerzas:
*   **Evitar demasiados servicios**, porque aumentaría el costo y la complejidad.
*   **Evitar servicios demasiado grandes**, porque reduciría la cohesión y aumentaría el acoplamiento.
## Decisión
Se decide implementar Geojana mediante **seis servicios principales**, comunicados mediante REST a través del API Gateway y respaldados por una base de datos compartida PostgreSQL/PostGIS o Supabase.
Los servicios definidos son:
1. **API Gateway**
2. **Identity & Access Service**
3. **Sighting Service**
4. **Institution Service**
5. **Map Service**
6. **Content Service**
7. **Analytics Service**
Aunque son siete componentes nombrados, el **API Gateway** se considera una capa técnica de entrada, no un servicio de dominio. Por lo tanto, la arquitectura mantiene **seis servicios funcionales principales**.
La decisión se basa en los siguientes criterios:
*   Separar servicios por **capacidad de negocio**.
*   Mantener **alta cohesión**, agrupando funcionalidades que cambian por razones similares.
*   Mantener **bajo acoplamiento**, evitando que un servicio conozca detalles internos de otro.
*   Evitar microservicios demasiado finos.
*   Mantener base de datos compartida por bajo costo y consistencia.
*   Usar APIs REST documentadas como contratos entre frontend, gateway y servicios.
* * *
# Servicios definidos
## 1\. API Gateway
### Responsabilidad
Actuar como punto único de entrada para las aplicaciones frontend de Geojana.
### Funciones principales
*   Recibir solicitudes desde la PWA ciudadana y la plataforma administrativa.
*   Validar token de sesión.
*   Redirigir solicitudes al servicio correspondiente.
*   Centralizar CORS, rate limiting y manejo uniforme de errores.
*   Ocultar al frontend la ubicación real de los servicios internos.
*   Registrar logs básicos de entrada y salida.
### No debe encargarse de
*   Crear reportes.
*   Gestionar usuarios.
*   Ejecutar reglas de derivación institucional.
*   Calcular métricas.
*   Consumir proveedores geoespaciales directamente.
### Justificación
El API Gateway reduce el acoplamiento entre frontend y backend. El frontend no necesita conocer cada servicio interno, y los servicios pueden cambiar su ubicación o estructura sin afectar directamente a la PWA. Esta decisión es coherente con ADR-2, donde se establece que las PWAs deben consumir servicios mediante una capa de API o Gateway.
* * *
## 2\. Identity & Access Service
### Responsabilidad
Gestionar identidad, perfiles, roles, permisos y puntos de confianza de usuarios.
### Funciones principales
*   Registrar usuarios base.
*   Gestionar perfiles de usuario, institución y administrador.
*   Validar roles: Usuario Base, Institución y Administrador.
*   Administrar permisos de acceso.
*   Gestionar estados de cuenta: activo, suspendido o bloqueado.
*   Mantener puntos de confianza de usuarios.
*   Consultar historial básico de participación del usuario.
*   Asociar usuarios institucionales a una institución existente.
### No debe encargarse de
*   Crear o modificar reportes.
*   Derivar reportes.
*   Gestionar puntos de interés.
*   Calcular métricas del dashboard.
*   Editar contenido educativo.
### Requerimientos asociados
RF11, RF12, RF13, RF14, RF16, RF17.
### Justificación
Este servicio tiene alta cohesión porque todas sus funciones se relacionan con **quién es el usuario y qué puede hacer**. Además, separa claramente la autorización del resto del dominio. Geojana contempla actores con permisos diferenciados: usuario base, institución, administrador y sistema de geolocalización.
* * *
## 3\. Sighting Service
### Responsabilidad
Gestionar el ciclo de vida de los reportes geolocalizados.
### Funciones principales
*   Crear reportes de avistamiento, amenaza y emergencia.
*   Registrar coordenadas GPS del incidente.
*   Guardar datos del formulario de reporte.
*   Asociar evidencia fotográfica al reporte.
*   Gestionar estados del reporte: recibido, procesando, resuelto y archivado.
*   Registrar historial y trazabilidad del reporte.
*   Permitir validaciones comunitarias.
*   Permitir marcas de falso o duplicado.
*   Enviar reportes conflictivos a revisión administrativa.
*   Consultar reportes por estado, tipo, fecha, especie, usuario o institución.
*   Consultar reportes cercanos mediante PostGIS.
### No debe encargarse de
*   Crear usuarios o instituciones.
*   Definir reglas de competencia institucional.
*   Consumir Nominatim, OpenStreetMap o proveedores externos.
*   Gestionar guías educativas.
*   Calcular dashboards agregados complejos.
*   Administrar puntos de interés institucionales de forma principal.
### Requerimientos asociados
RF04, RF05, RF06, RF08, RF14, RF15, RF18, RF19, RF22, RF23, RF24.
### Justificación
Este servicio queda enfocado en una sola capacidad central: **el reporte de fauna y su ciclo de vida**. Así se evita que se convierta en un servicio demasiado grande. La derivación institucional se coordina con el Institution Service y la validación geográfica se coordina con el Map Service.
* * *
## 4\. Institution Service
### Responsabilidad
Gestionar instituciones, competencias territoriales, puntos de interés y reglas de derivación.
### Funciones principales
*   Crear, editar y desactivar instituciones.
*   Mantener datos de contacto institucional.
*   Registrar zonas de cobertura o jurisdicción.
*   Asociar tipos de incidente a instituciones competentes.
*   Determinar qué institución debe recibir un reporte.
*   Mantener institución de respaldo si no existe coincidencia precisa.
*   Gestionar puntos de interés relacionados con instituciones.
*   Crear, editar y ocultar puntos de interés en el mapa.
*   Consultar centros de rehabilitación, veterinarias, refugios, zonas de riesgo o áreas protegidas.
*   Entregar al Sighting Service la institución sugerida para un reporte.
### No debe encargarse de
*   Crear reportes.
*   Cambiar estados de reportes.
*   Gestionar usuarios finales.
*   Renderizar mapas.
*   Consumir directamente proveedores externos de mapas.
*   Calcular métricas del dashboard.
### Requerimientos asociados
RF02, RF03, RF08, RF26, RF27.
### Justificación
Este servicio mejora la cohesión del diseño porque agrupa todo lo relacionado con **instituciones, cobertura territorial, puntos de interés y derivación**. Estas funciones cambian por razones similares: incorporación de nuevas instituciones, cambios de jurisdicción, nuevos centros de atención o modificaciones en reglas territoriales.
Separar esta lógica del Sighting Service reduce acoplamiento. El reporte no necesita conocer internamente cómo se calcula la institución competente; solo solicita la derivación al Institution Service.
* * *
## 5\. Map Service
### Responsabilidad
Centralizar la integración geoespacial externa y desacoplar el sistema de proveedores de mapas.
### Funciones principales
*   Ejecutar geocodificación.
*   Ejecutar reverse geocoding.
*   Normalizar respuestas geográficas.
*   Validar coordenadas.
*   Encapsular integración con Nominatim u otros proveedores.
*   Permitir fallback futuro entre proveedores.
*   Apoyar validaciones geográficas solicitadas por otros servicios.
*   Evitar que los servicios de dominio consuman directamente proveedores externos.
### No debe encargarse de
*   Guardar reportes.
*   Crear puntos de interés.
*   Gestionar usuarios.
*   Definir reglas institucionales.
*   Calcular métricas.
*   Renderizar el mapa visual.
### Requerimientos asociados
RF01, RF02, RF03, RF04, RF08.
### Justificación
ADR-10 establece una separación clara entre renderizado, geocodificación y dominio. El frontend usa Leaflet para renderizar, los Tile Providers entregan imágenes, y el Map Service abstrae la integración con proveedores como Nominatim u OpenStreetMap.
Por bajo acoplamiento, ningún servicio de dominio debe depender directamente de proveedores geoespaciales externos.
* * *
## 6\. Content Service
### Responsabilidad
Gestionar contenido educativo, protocolos y guías de acción.
### Funciones principales
*   Crear, editar y eliminar guías de emergencia.
*   Crear, editar y eliminar fichas de fauna.
*   Mantener información de especies.
*   Mantener protocolos por tipo de incidente.
*   Entregar instrucciones de acción inmediata al finalizar un reporte.
*   Publicar contenido educativo para la PWA ciudadana.
*   Asociar protocolos a categorías de reporte: avistamiento, amenaza y emergencia.
### No debe encargarse de
*   Crear reportes.
*   Gestionar usuarios.
*   Derivar instituciones.
*   Calcular métricas.
*   Administrar puntos de interés.
*   Ejecutar lógica geoespacial.
### Requerimientos asociados
RF07, RF09, RF10, RF25.
### Justificación
Este servicio tiene alta cohesión porque agrupa información editorial y educativa. Su razón de cambio es distinta a la del dashboard y distinta a la de reportes. Por eso se separa del Analytics Service.
* * *
## 7\. Analytics Service
### Responsabilidad
Generar métricas, indicadores, filtros y exportaciones para instituciones y administradores.
### Funciones principales
*   Consultar métricas de reportes.
*   Generar KPIs para dashboard institucional y administrativo.
*   Filtrar datos por fecha, ubicación, tipo de incidente, especie y estado.
*   Generar datos para gráficos.
*   Exportar datos en CSV, Excel o PDF.
*   Calcular distribución territorial de incidentes.
*   Apoyar auditorías de consistencia entre reportes almacenados y reportes visualizados.
### No debe encargarse de
*   Crear reportes.
*   Cambiar estados de reportes.
*   Gestionar usuarios.
*   Crear contenido educativo.
*   Ejecutar derivación institucional.
*   Modificar puntos de interés.
### Requerimientos asociados
RF20, RF21.
### Justificación
Separar Analytics mejora la cohesión porque las consultas analíticas tienen una naturaleza distinta a las operaciones transaccionales. El Sighting Service registra y actualiza reportes; el Analytics Service consulta y agrega información para apoyar la toma de decisiones.
Esto también permite cuidar el escenario de fiabilidad que exige que los reportes sincronizados aparezcan en el dashboard en menos de 5 minutos.
* * *
# Distribución final de responsabilidades

| Servicio | Alta cohesión porque agrupa | Evita acoplamiento porque |
| ---| ---| --- |
| API Gateway | Entrada, seguridad de borde y enrutamiento | El frontend no conoce servicios internos |
| Identity & Access Service | Identidad, roles, permisos y confianza | Los demás servicios no gestionan permisos directamente |
| Sighting Service | Reportes, estados, validaciones y trazabilidad | No contiene reglas institucionales ni proveedores externos |
| Institution Service | Instituciones, cobertura, POI y derivación | Reportes no conocen detalles de jurisdicción |
| Map Service | Geocodificación y proveedores externos | El dominio no depende de Nominatim/OSM |
| Content Service | Guías, protocolos y fauna | El contenido no se mezcla con reportes ni métricas |
| Analytics Service | Dashboard, indicadores y exportación | Las consultas analíticas no sobrecargan el servicio de reportes |

* * *
# Flujo principal de creación de reporte
1. El usuario abre la PWA.
2. El frontend obtiene coordenadas GPS.
3. El usuario completa el formulario de reporte.
4. La PWA envía la solicitud al API Gateway.
5. El API Gateway valida el token y redirige al Sighting Service.
6. El Sighting Service registra el reporte.
7. El Sighting Service solicita al Institution Service la institución competente.
8. El Institution Service puede apoyarse en PostGIS y, si requiere validación externa, solicitar apoyo al Map Service.
9. El Sighting Service guarda la derivación.
10. El Content Service entrega las instrucciones de acción correspondientes.
11. El Analytics Service reflejará el reporte en dashboard dentro del tiempo definido.
* * *
# Consecuencias
## Positivas
**Mayor cohesión:** cada servicio tiene una razón de cambio clara. Reportes, usuarios, instituciones, mapas, contenido y métricas quedan separados.
**Menor acoplamiento:** los servicios no necesitan conocer detalles internos de otros. Por ejemplo, Sighting Service no conoce cómo se calcula una jurisdicción, solo solicita la institución competente.
**Mejor mantenibilidad:** si cambia la lógica de derivación institucional, se modifica Institution Service, no todo el sistema.
**Mejor capacidad de prueba:** las reglas de reporte, permisos, derivación, geocodificación y dashboard pueden probarse por separado.
**Coherencia con ADR-10:** la integración geoespacial queda aislada en Map Service, evitando dependencia directa con proveedores externos.
**Complejidad controlada:** no se crean servicios muy pequeños como Media Service, Sync Service o POI Service separados. Esos quedan integrados en servicios más grandes pero coherentes.
## Negativas
**Más servicios que la versión acotada anterior:** se pasa de cinco a siete componentes, aunque solo seis son servicios de dominio.
**Mayor esfuerzo de documentación:** cada servicio requiere endpoints, contratos y responsabilidades claras.
**Base de datos compartida:** reduce costos, pero exige disciplina para que cada servicio acceda solo a las tablas que le corresponden.
**Analytics puede depender de datos de varios servicios:** debe manejarse preferentemente mediante vistas, consultas controladas o endpoints de lectura para no generar acoplamiento fuerte.
**Institution Service concentra POI y derivación:** si en el futuro los puntos de interés crecen mucho, podrían separarse en un POI Service.
* * *
# Cumplimiento

| Criterio | Forma de verificación |
| ---| --- |
| Cohesión por servicio | Cada servicio debe tener un README indicando su responsabilidad principal y responsabilidades excluidas |
| Bajo acoplamiento | Ningún servicio debe importar código interno de otro servicio |
| Acceso centralizado | El frontend debe consumir únicamente el API Gateway |
| Contratos REST | Cada servicio debe documentar sus endpoints mediante OpenAPI/Swagger |
| Desacoplamiento geoespacial | Ningún servicio de dominio debe consumir directamente Nominatim, OSM, HERE Maps u otro proveedor |
| Separación de reportes e instituciones | Sighting Service no debe contener reglas de jurisdicción institucional |
| Separación de contenido y métricas | Content Service no debe calcular dashboard y Analytics Service no debe editar guías |
| Dashboard actualizado | El 99% de reportes sincronizados debe aparecer en dashboard en menos de 5 minutos |
| Derivación correcta | La asignación de institución competente debe alcanzar ≥ 99% de acierto en pruebas definidas |
| Offline | Los reportes guardados localmente deben sincronizarse sin pérdida al recuperar conexión |
| Pruebas de integración | Cada servicio debe tener pruebas mínimas sobre sus endpoints principales |

* * *
# Decisión final
Se acepta una definición corregida de servicios para Geojana basada en **alta cohesión y bajo acoplamiento**:

```gherkin
Frontend PWA Ciudadana / Plataforma Institucional-Administrativa
        ↓
API Gateway
        ↓
-------------------------------------------------
| Identity & Access Service                      |
| Sighting Service                               |
| Institution Service                            |
| Map Service                                    |
| Content Service                                |
| Analytics Service                              |
-------------------------------------------------
        ↓
Base de datos compartida PostgreSQL/PostGIS / Supabase


```

Esta versión mejora la distribución anterior porque evita que el Sighting Service concentre demasiadas responsabilidades y separa contenido educativo de analítica. A la vez, mantiene una cantidad razonable de servicios para no caer en una arquitectura de microservicios compleja o costosa.
## Notas
Autor: Belén, Valentina & Viviana
Día de publicación: 2-06-2026
Última actualización: 4-06-2026