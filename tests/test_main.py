import pytest
from fastapi.testclient import TestClient
from main import app
from bson.objectid import ObjectId

client = TestClient(app)

# --- FIXTURES (MOCKS) ---
# Aquí inyectamos comportamientos falsos para no usar MongoDB ni Ollama reales

@pytest.fixture
def mock_db(mocker):
    """Mockeamos las funciones de db_repo que el router importa y usa."""
    mocker.patch("app.routers.obtener_todos", return_value=[{"_id": "fake_id_123", "filename": "test.pdf"}])
    mocker.patch("app.routers.obtener_por_id", return_value={"_id": ObjectId("507f1f77bcf86cd799439011"), "filename": "test.pdf"})
    
    # Estas son las que movimos a pdf_service
    mocker.patch("service.pdf_service.obtener_por_checksum", return_value=None)
    
    class FakeInsertResult:
        inserted_id = ObjectId("507f1f77bcf86cd799439011")
    mocker.patch("service.pdf_service.guardar_documento", return_value=FakeInsertResult())
    
    class FakeUpdateResult:
        matched_count = 1
    mocker.patch("app.routers.actualizar_nombre", return_value=FakeUpdateResult())
    
    class FakeDeleteResult:
        deleted_count = 1
    mocker.patch("app.routers.eliminar_documento", return_value=FakeDeleteResult())

@pytest.fixture
def mock_ollama(mocker):
    """Mockeamos la función que se comunica con Ollama en el service"""
    mocker.patch("service.pdf_service.generar_resumen_ia", return_value="Resumen falso generado por mock.")

# --- TESTS ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_subida_exitosa(mock_db, mock_ollama):
    # Usamos el PDF real (dummy) creado por el equipo 1 para que pdfplumber no tire Error 500
    with open("tests/dummy.pdf", "rb") as f:
        contenido_pdf = f.read()
        
    response = client.post(
        "/upload",
        files={"file": ("dummy.pdf", contenido_pdf, "application/pdf")}
    )
    
    assert response.status_code == 200
    datos = response.json()
    assert "id" in datos
    assert datos["mensaje"] == "PDF subido, validado y resumido con IA exitosamente."

def test_subida_duplicada(mocker, mock_ollama):
    # Forzamos a que el sistema crea que ya existe un documento con el mismo checksum
    mocker.patch("service.pdf_service.obtener_por_checksum", return_value={"_id": "fake_id_123"})
    
    # Abrimos de nuevo el archivo real para pasarlo en la petición
    with open("tests/dummy.pdf", "rb") as f:
        contenido_pdf = f.read()
    
    response = client.post(
        "/upload",
        files={"file": ("dummy.pdf", contenido_pdf, "application/pdf")}
    )
    
    # Debe saltar el 'patovica' y dar Error 409
    assert response.status_code == 409

def test_error_tamano():
    contenido_pesado = b"0" * (6 * 1024 * 1024) # 6 MB
    response = client.post(
        "/upload",
        files={"file": ("archivo_pesado.pdf", contenido_pesado, "application/pdf")}
    )
    assert response.status_code == 400
    assert "demasiado grande" in response.json()["detail"]

def test_get_documents(mock_db):
    response = client.get("/documents")
    assert response.status_code == 200
    assert "documentos" in response.json()

def test_patch_document(mock_db):
    fake_id = "507f1f77bcf86cd799439011"
    response = client.patch(
        f"/documents/{fake_id}",
        json={"nuevo_nombre": "nombre_cambiado.pdf"}
    )
    assert response.status_code == 200
    assert "actualizado" in response.json()["mensaje"]

def test_delete_document(mock_db, mocker):
    fake_id = "507f1f77bcf86cd799439011"
    response = client.delete(f"/documents/{fake_id}")
    assert response.status_code == 200
    
    # Para el assert final de que tira 404, mockeamos que ahora no encuentra nada
    mocker.patch("app.routers.obtener_por_id", return_value=None)
    response_verificacion = client.get(f"/documents/{fake_id}")
    assert response_verificacion.status_code == 404
