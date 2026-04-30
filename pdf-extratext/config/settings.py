from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Definimos las variables que queremos leer del .env
    app_name: str = "API"

    mongo_url: str
    db_name: str
    ollama_url: str

    model_config = SettingsConfigDict(env_file=".env")

# Creamos una variable llamada 'settings' que tiene toda la info cargada
settings = Settings()