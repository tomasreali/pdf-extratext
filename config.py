from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Definimos las variables que queremos leer del .env
    app_name: str = "API"

    class Config:
        env_file = ".env"

# Creamos una variable llamada 'settings' que tiene toda la info cargada
settings = Settings()