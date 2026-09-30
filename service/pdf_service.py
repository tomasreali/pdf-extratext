import hashlib
import os
import pdfplumber # <-- Importante
import io         # <-- Importante
from ollama import Client
from fastapi import HTTPException
from app.models.documento import Documento
from repository.db_repo import (
    obtener_por_checksum, guardar_documento,
    obtener_todos, obtener_por_id, actualizar_nombre, eliminar_documento
)


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
cliente_ia = Client(host=OLLAMA_URL)

def calcular_checksum(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()

# --- ESTA ES LA FUNCIÓN NUEVA Y REAL ---
def extraer_texto_real(contenido_pdf: bytes) -> str:
    texto_completo = ""
    # Abrimos los bytes del PDF en memoria
    with pdfplumber.open(io.BytesIO(contenido_pdf)) as pdf:
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"
    return texto_completo

def generar_resumen_ia(texto: str) -> str:
    # Si el texto es muy corto o está vacío, le avisamos para que no falle
    if not texto or len(texto.strip()) < 10:
        return "El documento parece estar vacío o no contiene texto extraíble."

    prompt = f"Haz un resumen claro, conciso y en español del siguiente texto:\n\n{texto}"
    try:
        respuesta = cliente_ia.generate(model='llama3.2', prompt=prompt)
        return respuesta['response']
    except Exception as e:
        return f"Error con la IA: {str(e)}"

def procesar_archivo(contenido: bytes, filename: str, content_type: str) -> Documento:
    # 1. Validación de extensión
    es_pdf = filename.endswith(".pdf")
    es_mime_pdf = content_type == "application/pdf"
    if not es_pdf and not es_mime_pdf:
        raise HTTPException(status_code=400, detail="El archivo debe ser un documento PDF válido.")
    
    # 2. Validación de tamaño
    TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(status_code=400, detail="El archivo es demasiado grande. El máximo permitido es 5MB.")

    # 3. Verificación de duplicados (Checksum)
    checksum_calculado = calcular_checksum(contenido)
    if obtener_por_checksum(checksum_calculado):
        raise HTTPException(status_code=409, detail="Este documento ya fue subido y procesado previamente.")
    
    # 4. Extracción de texto
    texto_extraido = extraer_texto_real(contenido) 
    
    # 5. Generación de resumen con la IA
    resumen_generado = generar_resumen_ia(texto_extraido)
    
    # 6. Crear el objeto Documento
    documento = Documento(
        filename=filename,
        text=texto_extraido,
        resumen=resumen_generado,
        checksum=checksum_calculado
    )
    
    # 7. Persistencia en BD (Pasamos el documento como dict para compatibilidad con la BD)
    resultado = guardar_documento(documento.model_dump(exclude_none=True))
    
    # 8. Asignar el ID generado por Mongo
    documento.id = str(resultado.inserted_id)
    
    return documento

# Estas funciones permiten que el Router hable con el Repositorio
# pasando siempre por la capa de Service, respetando la arquitectura de 3 capas.

def listar_documentos():
    """Obtiene todos los documentos de la base de datos."""
    return obtener_todos()

def buscar_documento_por_id(doc_id: str):
    """Busca un documento específico por su ID."""
    doc = obtener_por_id(doc_id)
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def modificar_nombre_documento(doc_id: str, nuevo_nombre: str):
    """Actualiza el nombre de un documento existente."""
    return actualizar_nombre(doc_id, nuevo_nombre)

def borrar_documento(doc_id: str):
    """Elimina un documento de la base de datos."""
    return eliminar_documento(doc_id)