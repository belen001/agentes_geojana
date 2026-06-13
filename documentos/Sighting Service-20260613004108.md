# Sighting Service

# Endpoints — Sighting Service
* * *
# **Reportes**

> Se definen dos variantes del objeto reporte según el contexto de uso:

### `reportList` — usado en respuestas de colección (GET /reports, GET /reports/my-reports)
Versión liviana para renderizar tarjetas. No incluye descripción ni datos del reportante.

```json
{
  "id": "uuid",
  "status": "pendiente | enviado | procesando | resuelto | falso",
  "animalCount": "int",
  "reportPhotoUrl": "string | null",
  "latitude": "float",
  "longitude": "float",
  "createdAt": "datetime",
  "incidentType": {
    "id": "int",
    "name": "string",
    "category": "avistamiento | emergencia | amenaza"
  },
  "species": {
    "id": "int",
    "commonName": "string",
    "animalGroup": "mamífero | ave | reptil | otro"
  }
}
```

> `species` es `null` si el usuario no identificó la especie al reportar.
* * *

### `reportDetail` — usado en respuestas de objeto único (GET /:id, POST, PATCH /status)
Versión completa para la vista de detalle. Incluye todos los sub-objetos relevantes.

```json
{
  "id": "uuid",
  "status": "pendiente | enviado | procesando | resuelto | falso",
  "animalCount": "int",
  "description": "string",
  "reportPhotoUrl": "string | null",
  "latitude": "float",
  "longitude": "float",
  "createdAt": "datetime",
  "reporter": {
    "id": "uuid",
    "name": "string",
    "cellphoneNumber": "string",
    "trustPoints": "int"
  },
  "incidentType": {
    "id": "int",
    "name": "string",
    "category": "avistamiento | emergencia | amenaza"
  },
  "species": {
    "id": "int",
    "commonName": "string",
    "scientificName": "string",
    "animalGroup": "mamífero | ave | reptil | otro",
    "photoUrl": "string | null"
  },
  "assignedInstitution": {
    "id": "int",
    "name": "string",
    "emergencyPhone": "string"
  },
  "recomendatedAction": {
    "id": "int",
    "title": "string",
    "type": "reporte | catalogo"
  }
}
```

> `species`, `assignedInstitution` y `recomendatedAction` son `null` si aún no han sido asignados.
* * *

## **POST /reports**
Crea un nuevo reporte y retorna el objeto creado. El `reporterId` se extrae automáticamente del token de autenticación. El `status` inicial siempre es `enviado`.

URL Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: usuario\_base
Content-Type: application/json

Data Params:

```json
{
  "incidentTypeId": "int",
  "speciesId": "int | null",
  "animalCount": "int",
  "description": "string",
  "reportPhotoUrl": "string | null",
  "latitude": "float",
  "longitude": "float"
}
```

Success Response:
Code: 201
Content: `{ <reportDetail> }`

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **GET /reports**
Obtiene todos los reportes. Admite filtros opcionales por query params.

URL Params:
_Optional_: `status=[pendiente | enviado | procesando | resuelto | falso]`
_Optional_: `categoryId=[int]`
_Optional_: `incidentTypeId=[int]`
_Optional_: `assignedInstitutionId=[int]`
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin, institucion.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "reports": [
    {
      "id": "uuid",
      "status": "enviado",
      "animalCount": 2,
      "reportPhotoUrl": "https://...",
      "latitude": -38.7359,
      "longitude": -72.5904,
      "createdAt": "2026-06-08T10:00:00Z",
      "incidentType": {
        "id": 2,
        "name": "Atropello",
        "category": "emergencia"
      },
      "species": {
        "id": 3,
        "commonName": "Puma",
        "animalGroup": "mamífero"
      }
    },
    "..."
  ]
}
```

Error Response:
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **GET /reports/my-reports**
Obtiene todos los reportes enviados por el usuario autenticado, extraído desde el token.

URL Params:
None

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: usuario\_base
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "reports": [
    {
      "id": "uuid",
      "status": "procesando",
      "animalCount": 1,
      "reportPhotoUrl": null,
      "latitude": -38.7359,
      "longitude": -72.5904,
      "createdAt": "2026-06-08T10:00:00Z",
      "incidentType": {
        "id": 4,
        "name": "Especie invasora",
        "category": "amenaza"
      },
      "species": null
    },
    "..."
  ]
}
```

Error Response:
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **GET /reports/:id**
Obtiene un reporte específico por su ID con todos los sub-objetos expandidos.

URL Params:
_Required_: `id=[uuid]`

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: usuario\_base, institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "id": "3f7a1c2d-...",
  "status": "procesando",
  "animalCount": 1,
  "description": "Encontré un puma herido al costado de la ruta 5.",
  "reportPhotoUrl": "https://...",
  "latitude": -38.7359,
  "longitude": -72.5904,
  "createdAt": "2026-06-08T10:00:00Z",
  "reporter": {
    "id": "a1b2c3d4-...",
    "name": "Juan Pérez",
    "cellphoneNumber": "+56912345678",
    "trustPoints": 42
  },
  "incidentType": {
    "id": 2,
    "name": "Atropello",
    "category": "emergencia"
  },
  "species": {
    "id": 3,
    "commonName": "Puma",
    "scientificName": "Puma concolor",
    "animalGroup": "mamífero",
    "photoUrl": "https://..."
  },
  "assignedInstitution": {
    "id": 1,
    "name": "CONAF Araucanía",
    "emergency_phone": "+5645123456"
  },
  "recomendatedAction": {
    "id": 5,
    "title": "Protocolo fauna atropellada",
    "type": "reporte"
  }
}
```

Error Response:
Code: 404
Content: `{ "error": "Report doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **PATCH /reports/:id/status**
Actualiza el estado de un reporte y opcionalmente le asigna una institución o acción recomendada. Retorna el objeto completo actualizado.

URL Params:
_Required_: `id=[uuid]`

Data Params:

```json
{
  "status": "procesando | resuelto | falso",
  "assignedInstitutionId": "int | null",
  "recomendatedActionId": "int | null"
}
```

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin, institucion.
Content-Type: application/json

Success Response:
Code: 200
Content: `{ <report_detail> }`

Error Response:
Code: 400
Content: `{ "error": "Invalid status value" }`
OR
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 404
Content: `{ "error": "Report doesn't exist" }`
* * *

## **DELETE /reports/:id**
Realiza un soft delete del reporte especificado.

URL Params:
_Required_: `id=[uuid]`

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Success Response:
Code: 204

Error Response:
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 404
Content: `{ "error": "Report doesn't exist" }`
* * *

# **Validaciones de Reporte**

Objeto validación:

```json
{
  "reportId": "uuid",
  "user": {
    "id": "uuid",
    "name": "string",
    "trustPoints": "int"
  },
  "isValid": "boolean",
  "createdAt": "datetime"
}
```

> Se expande `user` con nombre y puntos de confianza para dar contexto sobre quién validó y cuánto peso tiene su validación.
* * *

## **POST /reports/:id/validations**
Agrega una validación de un usuario sobre un reporte existente. Un usuario no puede validar su propio reporte ni validar el mismo reporte dos veces.

URL Params:
_Required_: `id=[uuid]`

Data Params:

```json
{
  "isValid": "boolean"
}
```

Headers:
Authorization: Bearer `<Auth Token>`
Role: usuario\_base, institucion, admin.
Content-Type: application/json

Success Response:
Code: 201
Content:

```json
{
  "reportId": "3f7a1c2d-...",
  "user": {
    "id": "a1b2c3d4-...",
    "name": "María González",
    "trustPoints": 78
  },
  "isValid": true,
  "createdAt": "2026-06-08T11:30:00Z"
}
```

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 403
Content: `{ "error": "You cannot validate your own report" }`
OR
Code: 409
Content: `{ "error": "You have already validated this report" }`
OR
Code: 404
Content: `{ "error": "Report doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **GET /reports/:id/validations**
Obtiene todas las validaciones asociadas a un reporte específico con el resumen de conteos.

URL Params:
_Required_: `id=[uuid]`

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: usuario\_base, institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "total": 5,
  "valid": 4,
  "notValid": 1,
  "validation": [
    {
      "reportId": "3f7a1c2d-...",
      "user": {
        "id": "a1b2c3d4-...",
        "name": "María González",
        "trustPoints": 78
      },
      "isValid": true,
      "createdAt": "2026-06-08T11:30:00Z"
    },
    "..."
  ]
}
```

Error Response:
Code: 404
Content: `{ "error": "Report doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *