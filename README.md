# pdf-extratext

Extrae texto de un PDF proporcionado por el usuario y genera un resumen usando IA.

## Integrantes

Reali Tomás, Calvente Matías, Barros Nazareno, Parola Marcos, Rossi Emiliano, Del Pozo Mateo, Altava Julián

## Tecnología
- Python 3.12
- uv (manejo de dependencias)
- FastAPI (framework web)
- OLLAMA con llama3.2 (modelo de IA local)
- MongoDB (base de datos no relacional)

## Metodologías
- TDD
- 12 Factor App (primeros 6 principios)

## Principios de programación
- KISS, DRY, YAGNI, SOLID

## Estructura
- `app/` → Endpoints y modelos
- `service/` → Lógica de negocio
- `repository/` → Acceso a datos
- `config/` → Configuraciones

---

## Cómo ejecutar el proyecto en cualquier computadora.

Gracias a Docker, la aplicación está completamente empaquetada. No es necesario instalar Python, ni MongoDB, ni Ollama de forma local. Todo se ejecutará en contenedores aislados.

### Requisitos previos.

1. Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/).
   * *Nota para usuarios de Windows: Asegurarse de tener habilitada la Virtualización en la BIOS y el motor WSL2 activado.*
2. Tener instalado **Git**.

### Paso 1: Clonar el repositorio.

Abrir una terminal y descargar el proyecto ejecutando:
```
git clone https://github.com/tomasreali/pdf-extratext.git
```
Luego de que se descarguen todas las carpetas, ejecutar:
```
cd pdf-extratext
```
### Paso 2: Configurar variables de entorno.

En la raíz del proyecto (al mismo nivel que el archivo docker-compose.yml), crear un archivo llamado ".env" y pegar la siguiente configuración:

```env
APP_NAME="Extraccion PDF API"
MONGO_URL=mongodb://mongodb:27017
OLLAMA_URL=http://ollama:11434
DB_NAME="pdf_db"
```

### Paso 3: Levantar la infraestructura.

Asegurarse de tener Docker Desktop abierto y ejecutándose de fondo. Luego, en la terminal del proyecto, ejecutar:
```
docker-compose up --build -d
```
### Paso 4: Descargar el modelo de Inteligencia Artificial

Se necesita descargar el modelo de lenguaje Llama 3.2. En la misma terminal, ejecutar:
```
docker exec -it pdf_ollama ollama run llama3.2
```
Cuando aparezca el cursor >>> indicando que el chat inició, escribir /bye y presionar Enter para salir.

### Usar la API.

Para interactuar con ella, abrir un navegador web e ingresar a la documentación interactiva de FastAPI (Swagger): "http://localhost:8000/docs"

Para apagar el proyecto cuando se termine de usar, ejecutar:
```
docker-compose down
```
### Usar el Frontend

Para interactuar con el frontend, se debe dirigir a la carpeta "frontend", desplegarla y hacer click derecho en "index.html" y abrirlo con Live Server.