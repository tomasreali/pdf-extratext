from fastapi import FastAPI
from app.routers import router

app = FastAPI(title="PDF Extractor API")

# Enganchamos todas las rutas que mudamos a la otra carpeta
app.include_router(router)