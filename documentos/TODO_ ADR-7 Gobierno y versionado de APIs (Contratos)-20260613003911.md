# TODO: ADR-7 Gobierno y versionado de APIs (Contratos)

## Descripción
Definir cómo evolucionarán las APIs REST, asegurando compatibilidad entre frontend y servicios, documentación y estabilidad de contratos.
## Alternativas a evaluar
*   Versionado por URL (`/v1/`)
*   Versionado por headers
*   APIs sin versionado explícito
*   OpenAPI/Swagger centralizado
*   Contract Testing
## Métricas / criterios de evaluación
*   Compatibilidad hacia atrás
*   Facilidad de mantenimiento
*   Impacto de cambios en frontend
*   Claridad documental
*   Complejidad de implementación
*   Facilidad de pruebas de integración