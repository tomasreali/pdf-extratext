from fastapi import FastAPI, UploadFile, File, HTTPException
from config.settings import settings
from config.database import collection
from bson.objectid import ObjectId
from bson.errors import InvalidId
from config.database import db
import pdfplumber

app = FastAPI(title=settings.app_name)

# Función para extraer texto del PDF
def extraer_texto_pdf(archivo) -> str:
    texto_completo = ""
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"
    return texto_completo


@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "mensaje": "Servidor funcionando perfecto",
        "app": settings.app_name
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    
    es_pdf = file.filename.endswith(".pdf")
    es_mime_pdf = file.content_type == "application/pdf"

    if not es_pdf and not es_mime_pdf:
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un documento PDF válido."
        )

    # 🔹 Extraer texto
    texto_crudo = extraer_texto_pdf(file.file)

    # 🔹 Crear documento para Mongo
    documento = {
        "filename": file.filename,
        "texto": texto_crudo
    }

    # 🔹 Guardar en MongoDB
    resultado = collection.insert_one(documento)

    # 🔹 Responder con ID
    return {
        "mensaje": "PDF procesado y guardado correctamente",
        "filename": file.filename,
        "id": str(resultado.inserted_id)
    }

@app.get("/documents")
async def get_documents():
    # 1. Buscamos en la base de datos (ocultando el texto gigante)
    cursor = collection.find({}, {"texto": 0})
    
    documentos = []
    # 2. Recorremos uno por uno
    for doc in cursor:
        # 3. Convertimos el ObjectId a texto normal
        doc["_id"] = str(doc["_id"]) 
        documentos.append(doc)
        
    return documentos

# --- NUEVO: Subtareas 2 y 3 (Buscar un documento específico) ---
@app.get("/documents/{doc_id}")
def get_document_by_id(doc_id: str):
    documento = None
    
    # Intento 1: Lo buscamos como ObjectId (El formato nativo de Mongo)
    try:
        obj_id = ObjectId(doc_id)
        documento = db["documents"].find_one({"_id": obj_id})
    except InvalidId:
        pass # Si el formato no sirve para ObjectId, ignoramos y pasamos al Intento 2

    # Intento 2: Si no lo encontró, lo buscamos como String plano (texto)
    if not documento:
        documento = db["documents"].find_one({"_id": doc_id})
        
    # Subtarea 3: Si probamos de ambas formas y sigue sin estar, devolvemos el 404
    if not documento:
        raise HTTPException(status_code=404, detail="No se encontró ningún documento con ese ID.")
        
    # Si lo encontró, convertimos el ID a string para que FastAPI lo pueda mostrar en pantalla
    documento["_id"] = str(documento["_id"])
    return documento