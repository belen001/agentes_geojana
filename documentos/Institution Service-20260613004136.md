# Institution Service

# Institution Service

# Endpoints — Institution Service

> Este servicio cubre cuatro dominios relacionados: gestión de **Instituciones**, administración de **Puntos de Interés (POI)**, catálogo de **Tipos de Incidente** y un endpoint de **Derivación Institucional** consumido internamente por el Sighting Service al registrar un reporte.  
> Los endpoints GET están disponibles para todos los roles autenticados. Los endpoints de escritura (POST, PATCH, DELETE) son exclusivos del rol `admin`.
* * *

# **Instituciones**

> Se definen dos variantes del objeto según el contexto de uso:

### `institutionList` — usado en GET /institutions
Versión liviana para listar instituciones en dropdowns o listados administrativos. No incluye descripción ni coordenadas.

```json
{
  "id": "int",
  "name": "string",
  "emergencyPhone": "string"
}
```

### `institutionDetail` — usado en GET /institutions/:id, POST y PATCH
Versión completa con todos los campos persistidos.

```json
{
  "id": "int",
  "name": "string",
  "description": "string | null",
  "emergencyPhone": "string",
  "latitude": "float",
  "longitude": "float"
}
```

* * *

## **GET /institutions**
Obtiene todas las instituciones registradas en el sistema. Utilizado por el administrador para gestión y por otros servicios para construir listados de contacto.

URL Params:
None

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
  "institutions": [
    {
      "id": 1,
      "name": "CONAF Araucanía",
      "emergencyPhone": "+5645123456"
    },
    {
      "id": 2,
      "name": "SAG Región de La Araucanía",
      "emergencyPhone": "+5645987654"
    },
    "..."
  ]
}
```

Error Response:
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **GET /institutions/:id**
Obtiene el detalle completo de una institución específica.

URL Params:
_Required_: `id=[int]`

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
  "id": 1,
  "name": "CONAF Araucanía",
  "description": "Corporación Nacional Forestal, encargada de la protección de recursos naturales y fauna silvestre en la región.",
  "emergencyPhone": "+5645123456",
  "latitude": -38.7359,
  "longitude": -72.5904
}
```

Error Response:
Code: 404
Content: `{ "error": "Institution doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **POST /institutions**
Crea una nueva institución en el sistema.

URL Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Data Params:

```json
{
  "name": "string",
  "description": "string | null",
  "emergencyPhone": "string",
  "latitude": "float",
  "longitude": "float"
}
```

Success Response:
Code: 201
Content: `{ <institutionDetail> }`

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **PATCH /institutions/:id**
Actualiza los campos de una institución existente. Solo se modifican los campos enviados.

URL Params:
_Required_: `id=[int]`

Data Params:

```json
{
  "name": "string",
  "description": "string | null",
  "emergencyPhone": "string",
  "latitude": "float",
  "longitude": "float"
}
```

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Success Response:
Code: 200
Content: `{ <institutionDetail> }`

Error Response:
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 404
Content: `{ "error": "Institution doesn't exist" }`
* * *

## **DELETE /institutions/:id**
Elimina una institución del sistema. Realiza un soft delete.

URL Params:
_Required_: `id=[int]`

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
Content: `{ "error": "Institution doesn't exist" }`
* * *

# **Tipos de Incidente**

> Los tipos de incidente son el catálogo de referencia que utiliza el Sighting Service al crear reportes y el Institution Service para definir reglas de derivación. Cada tipo pertenece a una categoría (`avistamiento`, `emergencia` o `amenaza`).

### `incidentType` — usado en GET /incident-types y GET /incident-types/:id

```json
{
  "id": "int",
  "name": "string",
  "description": "string | null",
  "category": {
    "id": "int",
    "name": "avistamiento | emergencia | amenaza"
  }
}
```

* * *

## **GET /incident-types**
Obtiene todos los tipos de incidente. Se puede filtrar por categoría para poblar formularios y selectores en el frontend.

URL Params:
_Optional_: `categoryId=[int]`

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
  "incidentTypes": [
    {
      "id": 1,
      "name": "Avistamiento en zona urbana",
      "description": "Animal silvestre observado dentro de área poblada.",
      "category": {
        "id": 1,
        "name": "avistamiento"
      }
    },
    {
      "id": 2,
      "name": "Atropello",
      "description": "Animal herido o muerto por impacto vehicular.",
      "category": {
        "id": 2,
        "name": "emergencia"
      }
    },
    {
      "id": 3,
      "name": "Especie invasora",
      "description": "Presencia de especie exótica con potencial daño al ecosistema.",
      "category": {
        "id": 3,
        "name": "amenaza"
      }
    },
    "..."
  ]
}
```

Error Response:
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **POST /incident-types**
Crea un nuevo tipo de incidente y lo asocia a una categoría existente.

URL Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Data Params:

```json
{
  "name": "string",
  "description": "string | null",
  "categoryId": "int"
}
```

Success Response:
Code: 201
Content: `{ <incidentType> }`

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 400
Content: `{ "error": "Category doesn't exist" }`
OR
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **PATCH /incident-types/:id**
Actualiza los campos de un tipo de incidente existente. Solo se modifican los campos enviados.

URL Params:
_Required_: `id=[int]`

Data Params:

```json
{
  "name": "string",
  "description": "string | null",
  "categoryId": "int"
}
```

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Success Response:
Code: 200
Content: `{ <incidentType> }`

Error Response:
Code: 400
Content: `{ "error": "Category doesn't exist" }`
OR
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 404
Content: `{ "error": "Incident type doesn't exist" }`
* * *

## **DELETE /incident-types/:id**
Elimina un tipo de incidente del catálogo. Realiza un soft delete.

URL Params:
_Required_: `id=[int]`

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
Content: `{ "error": "Incident type doesn't exist" }`
* * *

# **Derivación Institucional**

> Este endpoint es consumido internamente por el **Sighting Service** al registrar un nuevo reporte. A partir de las coordenadas y el tipo de incidente, el Institution Service determina cuál es la institución competente y la retorna para que el Sighting Service la persista en el reporte.  
> `fallback: true` indica que no se encontró una coincidencia exacta de jurisdicción y se retorna la institución de respaldo configurada por defecto.

### `derivationResult` — usado en POST /institutions/derive

```json
{
  "institution": {
    "id": "int",
    "name": "string",
    "emergencyPhone": "string"
  },
  "fallback": "boolean"
}
```

> `institution` es `null` si no existe ninguna institución configurada en el sistema (incluyendo respaldo).
* * *

## **POST /institutions/derive**
Determina la institución competente para un reporte dado su ubicación y tipo de incidente. Utiliza PostGIS para verificar cobertura territorial y aplica la institución de respaldo si no hay coincidencia exacta.

URL Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin, institucion.
Content-Type: application/json

Data Params:

```json
{
  "latitude": "float",
  "longitude": "float",
  "incidentTypeId": "int"
}
```

Success Response:
Code: 200
Content:

```json
{
  "institution": {
    "id": 1,
    "name": "CONAF Araucanía",
    "emergencyPhone": "+5645123456"
  },
  "fallback": false
}
```

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 400
Content: `{ "error": "Incident type doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
# **Puntos de Interés**

> Se definen dos variantes según el uso: una liviana para los marcadores del mapa y una completa para el panel de información al tocar un marcador.

### `poiMarker` — usado en GET /point-of-interest
Versión mínima para renderizar los íconos en el mapa. Solo incluye lo necesario para posicionar y categorizar el marcador.

```json
{
  "id": "int",
  "name": "string",
  "category": "santuario | veterinaria | refugio | centro_rehabilitacion | otro",
  "latitude": "float",
  "longitude": "float"
}
```

### `poiDetail` — usado en GET /point-of-interest/:id, POST y PATCH
Versión completa para el panel lateral o popup de información.

```json
{
  "id": "int",
  "name": "string",
  "category": "santuario | veterinaria | refugio | centro_rehabilitacion | otro",
  "address": "string",
  "description": "string | null",
  "photoUrl": "string | null",
  "schedule": "string",
  "latitude": "float",
  "longitude": "float"
}
```

* * *

## **GET /**point-of-interest
Obtiene todos los puntos de interés para poblar el mapa. Se puede filtrar por categoría para activar/desactivar capas.

URL Params:
_Optional_: `category=[santuario | veterinaria | refugio | centro_rehabilitacion | otro]`

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
  "pointOfInterest": [
    {
      "id": 1,
      "name": "Centro de Rehabilitación CONAF",
      "category": "centro_rehabilitacion",
      "latitude": -38.7359,
      "longitude": -72.5904
    },
    {
      "id": 2,
      "name": "Clínica Veterinaria UACh",
      "category": "veterinaria",
      "latitude": -38.7481,
      "longitude": -72.6012
    },
    "..."
  ]
}
```

Error Response:
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **GET /**point-of-interest**/:id**
Obtiene el detalle completo de un punto de interés para mostrar en el panel de información.

URL Params:
_Required_: `id=[int]`

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
  "id": 1,
  "name": "Centro de Rehabilitación CONAF",
  "category": "centro_rehabilitacion",
  "address": "Av. Caupolicán 1234, Temuco, La Araucanía",
  "description": "Centro oficial de rehabilitación de fauna silvestre de la región.",
  "photorl": "https://...",
  "schedule": "Lun–Vie 09:00–18:00",
  "latitude": -38.7359,
  "longitude": -72.5904
}
```

Error Response:
Code: 404
Content: `{ "error": "Point of interest doesn't exist" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **POST /**point-of-interest
Crea un nuevo punto de interés en el mapa.

URL Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Data Params:

```json
{
  "name": "string",
  "category": "santuario | veterinaria | refugio | centro_rehabilitacion | otro",
  "address": "string",
  "description": "string | null",
  "photoUrl": "string | null",
  "schedule": "string",
  "latitude": "float",
  "longitude": "float"
}
```

Success Response:
Code: 201
Content: `{ <poiDetail> }`

Error Response:
Code: 400
Content: `{ "error": "Missing required fields" }`
OR
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Internal server error" }`
* * *

## **PATCH /**point-of-interest**/:id**
Actualiza los campos de un punto de interés. Solo se modifican los campos enviados.

URL Params:
_Required_: `id=[int]`

Data Params:

```json
{
  "name": "string",
  "category": "santuario | veterinaria | refugio | centro_rehabilitacion | otro",
  "address": "string",
  "description": "string | null",
  "photoUrl": "string | null",
  "schedule": "string",
  "latitude": "float",
  "longitude": "float"
}
```

Headers:
Authorization: Bearer `<Auth Token>`
Role: admin.
Content-Type: application/json

Success Response:
Code: 200
Content: `{ <poiDetail> }`

Error Response:
Code: 403
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 404
Content: `{ "error": "Point of interest doesn't exist" }`
* * *

## **DELETE /**point-of-interest**/:id**
Elimina un punto de interés del mapa. Realiza un soft delete.

URL Params:
_Required_: `id=[int]`

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
Content: `{ "error": "Point of interest doesn't exist" }`