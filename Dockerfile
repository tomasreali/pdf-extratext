# 1. Traemos una compu virtual que ya tiene Python 3.12 instalado (versión slim para que pese poco)
FROM python:3.12-slim

# 2. Como usamos 'uv' en vez de 'pip' puro, copiamos la herramienta uv directo al contenedor
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Le decimos a Docker: "A partir de acá, todo lo que hagamos va a ser adentro de una carpeta llamada /app"
WORKDIR /app

# 4. Copiamos TU archivo pyproject.toml de tu Windows a la carpeta /app del contenedor
COPY pyproject.toml .

# 5. Ejecutamos 'uv' para que instale FastAPI, pymongo, ollama, etc., sin crear entornos virtuales extra
RUN uv pip install --system -r pyproject.toml

# 6. Copiamos TODO el resto de tu código (main.py, la carpeta app, service, etc.) adentro del contenedor
COPY . .

# 7. Le avisamos a Docker que nuestra API se va a comunicar por la "puerta" (puerto) 8000
EXPOSE 8000

# 8. El último paso de la receta: el comando exacto para encender el servidor una vez que todo esté listo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]