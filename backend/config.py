from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite+pysqlite:///./pehchaanai.db",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="dev-only-change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    backend_cors_origins: str = Field(
        default=(
            "http://localhost:3000,http://localhost:5173,"
            "http://127.0.0.1:5173,http://192.168.0.123:5173"
        ),
        alias="BACKEND_CORS_ORIGINS",
    )

    # Directory (relative to process CWD) that holds reference corpus images.
    ref_images_dir: str = Field(
        default="FGNET/images",
        alias="REF_IMAGES_DIR",
    )

    # Face recognition model pack
    face_model_name: str = Field(
        default="buffalo_s",  # lighter model: faster on CPU, uses MobileFaceNet
        alias="FACE_MODEL_NAME",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
