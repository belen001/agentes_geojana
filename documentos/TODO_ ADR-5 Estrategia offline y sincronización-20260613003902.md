# TODO: ADR-5 Estrategia offline y sincronización

## \[POSPUESTO SEGUNDA ITERACIÓN\]
## Descripción
Definir cómo funcionará el sistema cuando no exista conectividad, incluyendo almacenamiento local, sincronización posterior, resolución de conflictos y recuperación ante fallos de red.
## Alternativas a evaluar
*   IndexedDB + Service Workers manuales
*   Dexie.js
*   PouchDB + CouchDB
*   Firebase Offline Sync
*   Cola local personalizada
## Métricas / criterios de evaluación
*   Tiempo de sincronización tras reconexión
*   Tasa de pérdida de datos
*   Capacidad de operación offline
*   Consumo de almacenamiento local
*   Complejidad de implementación
*   Manejo de conflictos
*   Persistencia de reportes críticos