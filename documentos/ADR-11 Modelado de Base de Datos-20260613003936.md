# ADR-11 Modelado de Base de Datos

# Situación
Propuesto
# Contexto
Se requería un modelo normalizado que soporte la arquitectura basada en servicios (ADR-2), que respete la separación de dominios (ADR-10) y que permita un control de acceso robusto mediante roles.
# Decisión
Se decide implementar un modelo de datos relacional normalizado en PostgreSQL/Supabase, dividiendo las entidades según su ciclo de vida y dominio de negocio. Las justificaciones de las estructuras principales son:
**1\. Separación de Identidad y Directorio Institucional (\`profiles\` e \`institutions\`):**
Se extrae la información pública de las instituciones a una tabla independiente (\`institutions\`). La tabla \`profiles\` actúa como la extensión de autenticación (vinculada al ID de Supabase Auth), permitiendo que múltiples usuarios individuales se asocien a una misma institución mediante la llave foránea \`institution\_id\`. Esto mejora la trazabilidad, la seguridad en la rotación de personal y permite usar a las instituciones como contactos en protocolos de emergencia.
**2\. Desacoplamiento de Eventos y Ubicaciones Estáticas (\`reports\` y \`points\_of\_interest\`):**
Se separan los incidentes ciudadanos (eventos) de los lugares físicos permanentes. Los reportes guardan sus propias coordenadas sin depender de una tabla intermedia de puntos, optimizando las consultas espaciales. Los lugares fijos se almacenan en \`points\_of\_interest\`, evitando campos nulos innecesarios. Ambos se unificarán visualmente en el frontend o mediante vistas SQL.
**3\. Catálogos Centralizados (\`species\` y \`emergency\_protocols\`):**
Para evitar la redundancia de datos y textos extensos en cada reporte, la información taxonómica de la fauna y los pasos de acción ante emergencias se normalizan en tablas de catálogo. La tabla \`reports\` solo almacena los identificadores (llaves foráneas) correspondientes.
**4\. Validación Comunitaria (\`report\_validations\`):**
En lugar de utilizar un contador estático de validaciones en la tabla de reportes, se crea una tabla relacional que asocia el reporte con el usuario que lo valida. Esto asegura la transparencia (quién validó qué) y previene la duplicidad de votos de un mismo usuario.
![](https://t90131044258.p.clickup-attachments.com/t90131044258/5b50f601-2e94-41ee-9969-f81700799e5a/geojana\(2\).png)
# Consecuencias
**Positivo (+):** Alta cohesión de datos. El modelo refleja directamente los servicios propuestos en ADR-6 y ADR-10 (Institution Service gestiona \`institutions\` y \`points\_of\_interest\`; Sighting Service gestiona \`reports\`).
**Positivo (+):** Mayor escalabilidad y facilidad para implementar políticas de seguridad a nivel de fila (RLS) en Supabase, ya que los roles y las instituciones están claramente delimitados en \`profiles\`.
**Positivo (+):** Reducción drástica del peso de la tabla \`reports\`, mejorando el rendimiento de consultas y la transferencia de datos hacia la PWA.
**Negativo (-):** Duplicidad parcial de datos de autenticación (email y password) en la tabla \`profiles\`. Al utilizar Supabase Auth, estas credenciales ya son gestionadas internamente por el proveedor, lo que requerirá triggers o sincronización manual para mantener consistencia.
**Negativo (-):** Para mostrar el mapa unificado con reportes y puntos de interés, el sistema requerirá consultas tipo UNION o la creación de vistas (Views) en la base de datos, incrementando levemente la complejidad de lectura.
# Cumplimiento
**Revisión de Esquema:** Verificar que la base de datos en Supabase se genere sin errores respetando las llaves primarias, foráneas y enums definidos en el DBML.
**Pruebas de Integridad:** Comprobar que no se puedan insertar reportes con especies inexistentes ni validaciones duplicadas por el mismo usuario.
**Validación de Consultas:** Medir que el cruce de datos (JOIN) entre ``reports`, `species`` y \`institutions\` para la vista de "Detalle de Reporte" se resuelva en tiempos aceptables para la PWA.
# Notas
Autor: [@VIVIANA ANDREA CASTRO PINCHEIRA](#user_mention#88040631)
Día de publicación: 08-06-2026
Última actualización: 08-06-2026