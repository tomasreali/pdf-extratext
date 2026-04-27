from fastapi import FastAPI, UploadFile, File, HTTPException
from config.settings import settings
from config.database import collection
from bson.objectid import ObjectId
from bson.errors import InvalidId
from config.database import db
import pdfplumber
import hashlib

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

def generar_resumen_mock(texto: str) -> str:
    return "Este es un resumen simulado del texto. Aca en el futuro ira la respuesta de la IA (ollama)"

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "mensaje": "Servidor funcionando perfecto",
        "app": settings.app_name
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Validación de extensión (Del Paso 3)
    es_pdf = file.filename.endswith(".pdf")
    es_mime_pdf = file.content_type == "application/pdf"
    if not es_pdf and not es_mime_pdf:
        raise HTTPException(status_code=400, detail="El archivo debe ser un documento PDF válido.")
    
    # Leemos el archivo en la memoria (lo necesitamos para pesar, hashear y extraer)
    contenido = await file.read()
    
    # --- NUEVO: Subtarea 1 (Validar tamaño máximo) ---
    # 5MB en bytes (5 * 1024 * 1024)
    LIMITE_MB = 5
    TAMANO_MAXIMO_BYTES = LIMITE_MB * 1024 * 1024
    
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=400, 
            detail=f"El archivo es demasiado grande. El máximo permitido es {LIMITE_MB}MB."
        )

    # --- NUEVO: Subtarea 2 (Calcular el Checksum) ---
    # Le sacamos la huella digital al contenido del archivo
    checksum_calculado = hashlib.sha256(contenido).hexdigest()

    # --- NUEVO: Subtarea 3 (Buscar duplicados en MongoDB) ---
    # Buscamos si ya existe algún documento con esta misma huella
    duplicado = db["documents"].find_one({"checksum": checksum_calculado})
    if duplicado:
        # 409 Conflict es el código HTTP ideal para "esto ya existe"
        raise HTTPException(
            status_code=409, 
            detail="Este documento ya fue subido y procesado previamente."
        )
    
    # --- Extracción (El Paso 4 de los chicos) ---
    # (Acá iría el código real de pdfplumber usando la variable 'contenido')
    texto_extraido = "Texto de prueba extraído del PDF..." 
    
    # --- NUEVO: Subtarea 4 (Llamar al mock) ---
    resumen_generado = generar_resumen_mock(texto_extraido)
    
    # --- NUEVO: Subtarea 5 (Guardar Checksum y Resumen en MongoDB) ---
    nuevo_documento = {
        "filename": file.filename,
        "content_type": file.content_type,
        "text": texto_extraido,
        "resumen": resumen_generado,
        "checksum": checksum_calculado # Guardamos la huella para futuras comparaciones
    }
    
    resultado = db["documents"].insert_one(nuevo_documento)
    
    return {
        "id": str(resultado.inserted_id), 
        "filename": file.filename,
        "checksum": checksum_calculado,
        "resumen": resumen_generado,
        "mensaje": "PDF subido, validado y guardado correctamente."
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