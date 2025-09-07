from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"   # <-- allow extra environment variables
    )

settings = Settings()