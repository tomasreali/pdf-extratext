from bson.objectid import ObjectId
from bson.errors import InvalidId
from config.database import db  # Asegúrense de que esta importación coincida con cómo lo tenían en main.py

def obtener_todos():
    cursor = db["documents"].find({}, {"text": 0})
    return [{**doc, "_id": str(doc["_id"])} for doc in cursor]

def obtener_por_id(doc_id: str):
    try:
        doc = db["documents"].find_one({"_id": ObjectId(doc_id)})
    except InvalidId:
        doc = db["documents"].find_one({"_id": doc_id}) # Fallback del paso 6
    return doc

def obtener_por_checksum(checksum: str):
    return db["documents"].find_one({"checksum": checksum})

def guardar_documento(documento: dict):
    return db["documents"].insert_one(documento)

def actualizar_nombre(doc_id: str, nuevo_nombre: str):
    try:
        return db["documents"].update_one({"_id": ObjectId(doc_id)}, {"$set": {"filename": nuevo_nombre}})
    except InvalidId:
        return None

def eliminar_documento(doc_id: str):
    try:
        return db["documents"].delete_one({"_id": ObjectId(doc_id)})
    except InvalidId:
        return None