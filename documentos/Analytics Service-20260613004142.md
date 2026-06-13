# Analytics Service

# Analytics Service

# Endpoints — Analytics Service

> Este servicio expone métricas, indicadores y datos de visualización para los dashboards institucional y administrativo de Geojana. Todos sus endpoints son de **solo lectura**: el servicio no crea ni modifica reportes, usuarios ni contenido.  
> **Alcance por rol:**`institucion`: visualiza únicamente métricas de los reportes que le han sido derivados. El `institutionId` se extrae automáticamente del token.`admin`: visualiza métricas globales del sistema. Puede restringir el scope a una institución específica mediante el parámetro `institutionId`.  
> Todos los endpoints admiten los filtros temporales opcionales `from` y `to`. Si no se especifican, se retornan los datos de los últimos 30 días.
* * *

# **Dashboard**

> Objeto `dashboardSummary` — usado en GET /analytics/summary

```json
{
  "total": "int",
  "byStatus": {
    "enviado": "int",
    "procesando": "int",
    "resuelto": "int",
    "falso": "int"
  },
  "byCategory": {
    "avistamiento": "int",
    "emergencia": "int",
    "amenaza": "int"
  },
  "avgResolutionHours": "float | null",
  "lastReportAt": "datetime | null"
}
```

> `avgResolutionHours` es `null` si no existen reportes con estado `resuelto` en el período. `lastReportAt` es `null` si no hay reportes en el período.
* * *

## **GET /analytics/summary**
Retorna los KPIs principales del período indicado. Es el endpoint principal que alimenta las tarjetas de métricas en la cabecera del dashboard institucional y administrativo.

URL Params:
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "total": 142,
  "byStatus": {
    "enviado": 64,
    "procesando": 40,
    "resuelto": 26,
    "falso": 12
  },
  "byCategory": {
    "avistamiento": 80,
    "emergencia": 35,
    "amenaza": 27
  },
  "avgResolutionHours": 1.4,
  "lastReportAt": "2026-06-08T14:32:00Z"
}
```

Error Response:
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

# **Distribución por Estado y Tipo**

> Los endpoints de esta sección retornan datos estructurados para alimentar gráficos de barras y de anillo en el dashboard.

### `statusBreakdown` — usado en GET /analytics/by-status

```json
{
  "total": "int",
  "breakdown": [
    {
      "status": "enviado | procesando | resuelto | falso",
      "count": "int",
      "percentage": "float"
    }
  ]
}
```

### `incidentTypeBreakdown` — usado en GET /analytics/by-incident-type

```json
{
  "breakdown": [
    {
      "incidentTypeId": "int",
      "incidentTypeName": "string",
      "category": "avistamiento | emergencia | amenaza",
      "count": "int"
    }
  ]
}
```

* * *

## **GET /analytics/by-status**
Retorna la distribución de reportes por estado con conteo y porcentaje sobre el total. Alimenta el gráfico de anillo del dashboard.

URL Params:
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "total": 142,
  "breakdown": [
    {
      "status": "enviado",
      "count": 64,
      "percentage": 45.1
    },
    {
      "status": "procesando",
      "count": 40,
      "percentage": 28.2
    },
    {
      "status": "resuelto",
      "count": 26,
      "percentage": 18.3
    },
    {
      "status": "falso",
      "count": 12,
      "percentage": 8.4
    }
  ]
}
```

Error Response:
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **GET /analytics/by-incident-type**
Retorna la distribución de reportes agrupados por tipo de incidente. Alimenta el gráfico de barras de tipologías del dashboard.

URL Params:
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `category=[avistamiento | emergencia | amenaza]`
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "breakdown": [
    {
      "incidentTypeId": 2,
      "incidentTypeName": "Atropello",
      "category": "emergencia",
      "count": 48
    },
    {
      "incidentTypeId": 1,
      "incidentTypeName": "Avistamiento en zona urbana",
      "category": "avistamiento",
      "count": 35
    },
    {
      "incidentTypeId": 3,
      "incidentTypeName": "Especie invasora",
      "category": "amenaza",
      "count": 22
    },
    "..."
  ]
}
```

Error Response:
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

# **Distribución por Especie y Territorio**

### `speciesBreakdown` — usado en GET /analytics/by-species

```json
{
  "breakdown": [
    {
      "speciesId": "int",
      "commonName": "string",
      "animalGroup": "mamífero | ave | reptil | otro",
      "count": "int"
    }
  ]
}
```

> Solo incluye reportes en los que el usuario identificó la especie. Los reportes con `speciesId` nulo se excluyen de este conteo.

### `communeBreakdown` — usado en GET /analytics/by-commune

```json
{
  "breakdown": [
    {
      "commune": "string",
      "count": "int"
    }
  ]
}
```

> La comuna se obtiene mediante reverse geocoding aplicado sobre las coordenadas del reporte. Si una coordenada no puede ser resuelta, el reporte se agrupa bajo `"commune": "Desconocida"`.
* * *

## **GET /analytics/by-species**
Retorna el ranking de especies más reportadas en el período. Alimenta el panel de distribución por especie del dashboard.

URL Params:
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `limit=[int]` _(por defecto: 10)_
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "breakdown": [
    {
      "speciesId": 3,
      "commonName": "Puma",
      "animalGroup": "mamífero",
      "count": 45
    },
    {
      "speciesId": 7,
      "commonName": "Huemul del Norte",
      "animalGroup": "mamífero",
      "count": 33
    },
    {
      "speciesId": 2,
      "commonName": "Zorro Culpeo",
      "animalGroup": "mamífero",
      "count": 28
    },
    "..."
  ]
}
```

Error Response:
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

## **GET /analytics/by-commune**
Retorna el ranking de comunas con mayor cantidad de reportes en el período. Alimenta el panel geográfico del dashboard.

URL Params:
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `limit=[int]` _(por defecto: 5)_
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.
Content-Type: application/json

Success Response:
Code: 200
Content:

```json
{
  "breakdown": [
    {
      "commune": "Temuco",
      "count": 56
    },
    {
      "commune": "Villarrica",
      "count": 34
    },
    {
      "commune": "Pucón",
      "count": 28
    },
    {
      "commune": "Victoria",
      "count": 14
    },
    {
      "commune": "Osorno",
      "count": 10
    }
  ]
}
```

Error Response:
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
* * *

# **Exportación**

> La exportación aplica los mismos filtros de fecha e institución que los demás endpoints. El servicio utiliza el **patrón Strategy** para generar el archivo en el formato solicitado: `csv` o `pdf`. La respuesta retorna el archivo directamente como descarga.

## **GET /analytics/export**
Genera y descarga un archivo con el detalle de los reportes del período, incluyendo estado, tipo de incidente, especie, ubicación y fecha. Responde con el archivo como stream descargable.

URL Params:
_Required_: `format=[csv | pdf]`
_Optional_: `from=[datetime]`
_Optional_: `to=[datetime]`
_Optional_: `status=[enviado | procesando | resuelto | falso]`
_Optional_: `category=[avistamiento | emergencia | amenaza]`
_Optional_: `institutionId=[int]` _(solo admin)_

Data Params:
None

Headers:
Authorization: Bearer `<Auth Token>`
Role: institucion, admin.

Success Response:
Code: 200
Headers:
`Content-Type: text/csv` o `Content-Type: application/pdf`
`Content-Disposition: attachment; filename="geojana_reportes_<timestamp>.<format>"`

Content: _(stream binario del archivo generado)_

Error Response:
Code: 400
Content: `{ "error": "format param is required" }`
OR
Code: 400
Content: `{ "error": "Invalid format. Allowed values: csv, pdf" }`
OR
Code: 400
Content: `{ "error": "institutionId filter is not allowed for this role" }`
OR
Code: 401
Content: `{ "error": "You are unauthorized to make this request." }`
OR
Code: 500
Content: `{ "error": "Export generation failed" }`