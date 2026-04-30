from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router

app = FastAPI(title="PDF Extractor API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se restringe, pero para la demo está perfecto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enganchamos todas las rutas que mudamos a la otra carpeta
app.include_router(router)