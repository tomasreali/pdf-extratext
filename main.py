from fastapi import FastAPI

# Inicializamos la aplicación
app = FastAPI()

# Creamos el endpoint GET en la ruta /health
@app.get("/health")
def health_check():
    return {"status": "ok"}