# Patrones de Diseño

## **1\. Nivel de Interfaz de Usuario (PWAs en Vue.js)**
Para las aplicaciones cliente, el patrón base es MVVM (Model-View-ViewModel), que viene integrado de forma nativa en Vue.js.
*   Propuesta: Patrón Command (Comportamiento)
    *   **Aplicación:** Utilizarlo para la creación de reportes offline. Cada acción de "Enviar Reporte" se encapsula como un objeto comando que se guarda en IndexedDB.
    *   **Criterio de Evaluación:** Si el sistema requiere una gestión compleja de reintentos y deshacer acciones (undo/redo) al recuperar señal.
    *   **Trade-off:** Añade una capa de abstracción adicional en el frontend, pero asegura la disponibilidad y la integridad del 99.9% de los reportes capturados sin conexión.
## **2\. Nivel de Entrada y Seguridad (API Gateway en Node.js)**
El Gateway actúa como el "Escudo Central" del sistema, implementando una combinación de patrones estructurales para garantizar la seguridad de borde y la simplicidad del cliente.
Implementación Híbrida: Patrón Facade + Patrón Proxy
A. Aplicación del Patrón Facade (Fachada)
*   Propósito: Proporcionar una interfaz única y simplificada a los seis servicios de dominio (Identity, Sighting, Institution, Map, Content y Analytics).
*   Funcionamiento en Geojana: Las aplicaciones frontend (PWAs) no necesitan conocer la ubicación, puertos o la complejidad de los contratos individuales de cada servicio interno. El Gateway ofrece un punto único de entrada que encapsula la lógica de red del backend, permitiendo que el sistema evolucione internamente sin afectar la integración de la interfaz de usuario.
B. Aplicación del Patrón Proxy (Intermediario)
*   Propósito: Interceptar todas las peticiones entrantes para realizar controles de acceso y validaciones antes de permitir que la solicitud llegue al servicio real \[Conversación previa\].
*   Funcionamiento en Geojana: Actúa como un Proxy de Seguridad que valida la firma y expiración de los tokens JWT emitidos por Supabase Auth mediante el plugin `@fastify/jwt`. Si la validación es exitosa, el Gateway "da la cara" por el servicio interno y redirige el tráfico de forma transparente mediante `@fastify/http-proxy`, ocultando la ubicación real y los puertos de los servicios de Python.
Beneficios del Enfoque Combinado
*   Consolidación de Preocupaciones Transversales: Se centraliza el manejo de CORS, Rate Limiting, encabezados de seguridad (Helmet) y la normalización de errores en una sola capa técnica.
*   Bajo Acoplamiento: Reduce la fricción entre frontend y backend, permitiendo que los servicios internos se desplieguen de forma independiente (Arquitectura Basada en Servicios).
*   Seguridad de Borde: Asegura que ninguna petición no autorizada (sin token válido) consuma recursos de procesamiento de los servicios de dominio.
Trade-offs y Mitigación
*   Punto Único de Fallo: Al centralizar todo el tráfico, el Gateway es crítico para la disponibilidad.
*   Mitigación: Se utiliza Fastify debido a su alto rendimiento (~35,000 req/s), lo que minimiza la latencia introducida por el enrutamiento y asegura que el Gateway no se convierta en un cuello de botella para la red en zonas rurales.
## **3\. Nivel de Servicios de Dominio (Python/FastAPI)**
Cada uno de los 6 servicios requiere patrones específicos para mantener la alta cohesión.
### **A. Map Service: Patrón Adapter (Estructural)**
*   Recomendación: Es indispensable para cumplir con el ADR-06 y el ADR-09.
*   Función: Traducir las interfaces de proveedores externos (OpenStreetMap, MapTiler, Nominatim) a un formato estándar que Geojana entienda.
*   Trade-off: Permite cambiar de proveedor de mapas sin tocar el resto de los servicios, pero introduce una pequeña latencia por la traducción de datos.
### **B. Analytics Service: Patrón Strategy (Comportamiento)**
*   Aplicación: Para la exportación de datos en múltiples formatos (CSV, Excel, PDF) definida en los requerimientos funcionales.
*   Justificación: Permite intercambiar el algoritmo de generación de archivos en tiempo de ejecución según la selección del usuario en el dashboard.
*   Trade-off: Evita condicionales (`if/else`) masivos, mejorando la mantenibilidad, aunque incrementa el número de clases pequeñas en el servicio.
### **C. Sighting & Identity Services: Patrón Observer (Comportamiento)**
*   Aplicación: Para la gestión de eventos internos. Cuando el `Sighting Service` registra un reporte validado, debe notificar al `Identity Service` para sumar "Puntos de Confianza" y al `Analytics Service` para actualizar el dashboard.
*   Evaluación: Crucial para cumplir la métrica de actualización del dashboard en menos de 5 minutos.
*   Trade-off: Desacopla los servicios (el Sighting no necesita saber qué hace el Analytics), pero puede dificultar el seguimiento del flujo de ejecución si hay muchos observadores encadenados.
### D. Identity & Access Service: Patrón Facade (Estructural)
*   Aplicación: Ocultar la complejidad de las reglas de gamificación y validación de roles institucionales complejos a los demás servicios.
## **Resumen para la Toma de Decisiones**

| Componente | Patrón Recomendado | Propósito Principal | Atributo de Calidad Beneficiado |
| ---| ---| ---| --- |
| Frontend | MVVM / Command | Gestión de estado y modo offline. | Usabilidad / Disponibilidad |
| Gateway | Facade / Proxy | Seguridad centralizada y punto de entrada. | Seguridad / Mantenibilidad |
| Map Service | Adapter | Desacoplamiento de proveedores externos. | Modificabilidad |
| Analytics | Strategy | Algoritmos de exportación variables. | Mantenibilidad / Flexibilidad |
| Sighting | Observer | Notificaciones asíncronas entre servicios. | Fiabilidad / Cohesión |

Evaluación Final: Para Geojana, el principio rector debe ser la concesión (trade-off) entre simplicidad y robustez. Dado que el equipo es universitario y el tiempo es limitado, se recomienda priorizar los patrones Adapter (para mapas) y Strategy (para exportaciones), ya que resuelven los riesgos técnicos más altos identificados en los ADRs.