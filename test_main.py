import pytest
from fastapi.testclient import TestClient
from main import app

# Creamos nuestro "cliente falso" para hacer peticiones a la API
client = TestClient(app)

# Variables globales para guardar el ID del documento de prueba
doc_id_prueba = None

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_subida_exitosa():
    global doc_id_prueba
    # Simulamos un PDF con un contenido falso
    contenido_pdf = b"Texto simulado para el test de subida"
    
    response = client.post(
        "/upload",
        files={"file": ("test_doc.pdf", contenido_pdf, "application/pdf")}
    )
    
    assert response.status_code == 200
    datos = response.json()
    assert "id" in datos
    assert datos["mensaje"] == "PDF subido, validado y guardado correctamente."
    
    # Guardamos el ID generado para usarlo en los siguientes tests
    doc_id_prueba = datos["id"]

def test_subida_duplicada():
    # Volvemos a subir EXACTAMENTE el mismo contenido falso
    contenido_pdf = b"Texto simulado para el test de subida"
    
    response = client.post(
        "/upload",
        files={"file": ("test_doc.pdf", contenido_pdf, "application/pdf")}
    )
    
    # Verificamos que el "patovica" del Paso 7 funcione y nos devuelva 409
    assert response.status_code == 409

def test_error_tamano():
    # Simulamos un archivo de más de 5MB (ej: 6MB de ceros)
    contenido_pesado = b"0" * (6 * 1024 * 1024)
    
    response = client.post(
        "/upload",
        files={"file": ("archivo_pesado.pdf", contenido_pesado, "application/pdf")}
    )
    
    # Verificamos que frene el archivo pesado
    assert response.status_code == 400
    assert "demasiado grande" in response.json()["detail"]

def test_get_documents():
    response = client.get("/documents")
    assert response.status_code == 200
    # Verificamos que la respuesta sea una lista (list)
    assert isinstance(response.json(), list)

def test_patch_document():
    global doc_id_prueba
    # Cambiamos el nombre del archivo que subimos en el primer test
    response = client.patch(
        f"/documents/{doc_id_prueba}",
        json={"nuevo_nombre": "nombre_cambiado.pdf"}
    )
    assert response.status_code == 200
    assert "actualizado" in response.json()["mensaje"]

def test_delete_document():
    global doc_id_prueba
    # Borramos el archivo de prueba para dejar la base de datos limpia
    response = client.delete(f"/documents/{doc_id_prueba}")
    assert response.status_code == 200
    
    # Verificamos que si lo intentamos buscar ahora, tire 404
    response_verificacion = client.get(f"/documents/{doc_id_prueba}")
    assert response_verificacion.status_code == 404