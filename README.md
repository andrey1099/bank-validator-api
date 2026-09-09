# Bank Validator API

API REST de validación de datos bancarios, con pipeline de integración continua y contenerización con Docker.

El servicio valida números de tarjeta mediante el algoritmo de Luhn y códigos IBAN de Costa Rica según el estándar ISO 13616. Todas las respuestas devuelven los números enmascarados, dejando visibles únicamente los últimos cuatro dígitos.

---

## Contenido

- [Motivación](#motivación)
- [Características](#características)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso](#uso)
- [Endpoints](#endpoints)
- [Pruebas](#pruebas)
- [Docker](#docker)
- [Pipeline de CI](#pipeline-de-ci)
- [Decisiones de diseño](#decisiones-de-diseño)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Motivación

Este proyecto nació como una forma de practicar prácticas de integración y despliegue continuo sobre un caso de uso realista. El dominio bancario resultó adecuado porque impone requisitos concretos de validación y de manejo de datos sensibles, lo que obliga a tomar decisiones de diseño que en un proyecto de ejemplo genérico no aparecerían.

---

## Características

- Validación de números de tarjeta con el algoritmo de Luhn
- Validación de IBAN costarricense, incluyendo la verificación de dígitos de control módulo 97
- Enmascarado de datos sensibles en todas las respuestas
- Endpoint de salud para monitoreo
- Documentación OpenAPI generada automáticamente
- 30 pruebas automatizadas
- Pipeline de CI con análisis estático, matriz de versiones y reporte de cobertura
- Contenerización con Docker y orquestación local con Docker Compose

---

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework | FastAPI |
| Servidor | Uvicorn |
| Validación de esquemas | Pydantic |
| Pruebas | pytest, pytest-cov |
| Análisis estático | Ruff |
| Contenedores | Docker, Docker Compose |
| Base de datos | PostgreSQL 16 |
| CI | GitHub Actions |

---

## Arquitectura

El proyecto separa la lógica de negocio de la capa de transporte.

El módulo `app/validators.py` contiene funciones puras que reciben texto y devuelven un resultado. No conoce HTTP, no importa FastAPI y no depende de ningún framework. Esto permite probar la lógica en milisegundos, sin levantar un servidor, y sustituir la capa web sin tocar las reglas de validación.

El módulo `app/main.py` expone esa lógica mediante endpoints REST. Se encarga del enrutamiento, la validación de las peticiones entrantes y la serialización de las respuestas.

```
Petición HTTP
      ↓
FastAPI resuelve la ruta
      ↓
Pydantic valida el cuerpo contra el modelo
      ↓  (si falla → 422 automático)
Handler llama a la lógica de validación
      ↓
Se construye la respuesta con el número enmascarado
      ↓
FastAPI serializa a JSON
```

---

## Instalación

### Requisitos

- Python 3.11 o superior
- Docker y Docker Compose, opcionales pero recomendados

### Entorno local

```bash
git clone https://github.com/andrey1099/bank-validator-api.git
cd bank-validator-api

python -m venv venv
```

Activar el entorno virtual:

```bash
# Linux o macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Uso

### Levantar el servidor

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.

La documentación interactiva se genera automáticamente y está en `http://localhost:8000/docs`. Desde ahí se pueden probar los endpoints sin necesidad de un cliente externo.

---

## Endpoints

### `GET /health`

Endpoint de salud para sistemas de monitoreo.

**Respuesta**

```json
{ "estado": "ok" }
```

### `POST /validar/tarjeta`

Valida un número de tarjeta mediante el algoritmo de Luhn.

**Petición**

```json
{ "numero": "4532015112830366" }
```

**Respuesta**

```json
{
  "valido": true,
  "valor": "************0366",
  "mensaje": "Numero valido"
}
```

### `POST /validar/iban`

Valida un IBAN de Costa Rica.

**Petición**

```json
{ "iban": "CR05015202001026284066" }
```

**Respuesta**

```json
{
  "valido": true,
  "valor": "******************4066",
  "mensaje": "IBAN valido"
}
```

### Códigos de respuesta

| Código | Significado |
|---|---|
| 200 | Petición procesada. El campo `valido` indica el resultado de la validación |
| 422 | El cuerpo de la petición no cumple el esquema esperado |

Conviene notar la distinción: un número inválido devuelve 200, porque la petición se procesó correctamente. El 422 se reserva para peticiones mal formadas, por ejemplo cuando falta un campo obligatorio.

---

## Pruebas

```bash
pytest -v
```

Con reporte de cobertura:

```bash
pytest --cov=app --cov-report=term
```

### Organización

Las pruebas se agrupan en tres categorías:

- **Casos válidos**, lo que el sistema debe aceptar
- **Casos inválidos**, lo que debe rechazar
- **Entradas mal formadas**, cadenas vacías, caracteres no numéricos, longitudes fuera de rango

La tercera categoría es la que suele omitirse y la que más problemas previene.

Se incluye además una prueba específica que verifica que el número original nunca aparezca en la respuesta, para garantizar que el enmascarado cumple su función.

---

## Docker

### Construir y ejecutar

```bash
docker build -t bank-validator-api .
docker run -p 8000:8000 bank-validator-api
```

### Con Docker Compose

Compose levanta la API junto con una base de datos PostgreSQL.

Antes de iniciar, crear el archivo de variables de entorno a partir del ejemplo:

```bash
cp .env.example .env
```

Definir el valor de `DB_PASSWORD` dentro de `.env` y levantar los servicios:

```bash
docker compose up -d
```

Comandos útiles:

```bash
docker compose ps          # estado de los servicios
docker compose logs -f api # logs en vivo
docker compose down        # detener y eliminar contenedores
docker compose down -v     # además elimina los volúmenes y sus datos
```

### Variables de entorno

| Variable | Descripción |
|---|---|
| `DB_PASSWORD` | Contraseña de PostgreSQL. Requerida |
| `APP_ENV` | Entorno de ejecución |
| `DB_HOST` | Host de la base de datos. Dentro de Compose se resuelve por el nombre del servicio |

El archivo `.env` está excluido del control de versiones. El archivo `.env.example` documenta las variables necesarias sin exponer valores.

---

## Pipeline de CI

Definido en `.github/workflows/ci.yml`, se ejecuta ante cada push y cada pull request hacia `main`.

```
lint  →  test  →  build
```

Los jobs están encadenados mediante `needs`, de modo que un fallo temprano evita gastar recursos en las etapas siguientes.

| Job | Función |
|---|---|
| `lint` | Análisis estático del código con Ruff |
| `test` | Pruebas automatizadas sobre una matriz de Python 3.11 y 3.12, en paralelo |
| `build` | Verifica que la aplicación cargue correctamente |

El job de pruebas genera un reporte de cobertura que se conserva como artefacto descargable desde la interfaz de GitHub Actions.

El pipeline se ejecuta sobre Ubuntu, lo que aporta una ventaja adicional durante el desarrollo en Windows: detecta dependencias del sistema operativo que de otro modo pasarían desapercibidas hasta el despliegue.

---

## Decisiones de diseño

### Uso de POST para las validaciones

Los endpoints de validación utilizan POST en lugar de GET, pese a no modificar estado. La razón es que los parámetros de una petición GET viajan en la URL, y las URLs quedan registradas en logs de servidores, proxies intermedios e historiales de navegador. Un número de tarjeta en la URL constituiría una fuga de datos sensibles.

### Enmascarado de datos en las respuestas

Aunque el cliente ya conoce el número que envió, la respuesta lo devuelve enmascarado. Las respuestas pueden quedar registradas en logs intermedios, y el estándar PCI DSS de la industria de pagos prohíbe el almacenamiento de números de tarjeta completos.

### Rechazo de números con dígitos repetidos

Un número compuesto por dígitos idénticos, como una secuencia de ceros, satisface el algoritmo de Luhn: la suma resultante es divisible entre diez. Sin embargo, no corresponde a una tarjeta real.

Este caso reveló una distinción importante durante el desarrollo. El algoritmo de Luhn detecta errores de digitación; no verifica que un número corresponda a una tarjeta existente. Se incorporó por tanto una regla de negocio explícita para rechazar estos casos, documentada como tal en el código.

### Orden de las instrucciones en el Dockerfile

El archivo copia `requirements.txt` e instala las dependencias antes de copiar el código fuente. Dado que cada instrucción genera una capa y que la modificación de una capa invalida todas las posteriores, este orden permite que la capa de dependencias permanezca en caché cuando solo cambia el código. La construcción pasa de minutos a segundos.

### Imagen base slim

Se utiliza `python:3.11-slim` en lugar de la imagen completa. La diferencia es de aproximadamente 250 MB frente a cerca de 1 GB. Además del ahorro en transferencia, una imagen con menos software instalado presenta una superficie de ataque menor.

### Configuración del host de escucha

El contenedor ejecuta Uvicorn con `--host 0.0.0.0`. El valor por defecto, `127.0.0.1`, limita la escucha a la interfaz local del contenedor, lo que impide alcanzar el servicio desde el exterior aun cuando el puerto esté correctamente mapeado.

---

## Estructura del proyecto

```
bank-validator-api/
├── .github/
│   └── workflows/
│       └── ci.yml              Pipeline de integración continua
├── app/
│   ├── __init__.py
│   ├── main.py                 Endpoints y modelos de datos
│   └── validators.py           Lógica de validación
├── tests/
│   ├── __init__.py
│   ├── test_api.py             Pruebas de los endpoints
│   └── test_validators.py      Pruebas de la lógica
├── .dockerignore
├── .env.example                Plantilla de variables de entorno
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Posibles mejoras

- Publicación automática de la imagen en un registro de contenedores
- Comprobaciones de salud en Compose, para asegurar que la base de datos acepte conexiones antes de iniciar la API
- Registro estructurado de eventos, verificando que los datos sensibles nunca se escriban en los logs
- Limitación de tasa de peticiones por cliente
- Persistencia del historial de validaciones en la base de datos

---

## Notas

Las tarjetas empleadas en las pruebas son números de prueba de uso público, diseñados para satisfacer el algoritmo de Luhn sin corresponder a cuentas reales.

Este proyecto tiene fines de aprendizaje y demostración.