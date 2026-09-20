from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Restaurant Booking API"
    database_url: str = "sqlite+aiosqlite:///./bookings.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()