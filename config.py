import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # ignore extra env vars (e.g. VITE_*)
    )
    # Application
    app_name: str = "Clinic CRM"
    app_version: str = "1.0.0"
    app_mode: Literal["offline", "online", "hybrid"] = "offline"

    # Local Database
    local_db_path: str = str(DATA_DIR / "clinic.db")

    # Supabase (Online Mode)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Sync Settings
    sync_interval_minutes: int = 5
    auto_sync_enabled: bool = True

    # SMS Settings
    sms_enabled: bool = False
    sms_api_key: str = ""
    sms_provider: str = "kavenegar"

settings = Settings()
