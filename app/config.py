from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Gastro Bot"
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = True
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"

    REPLICATE_API_TOKEN: str = ""
    REPLICATE_HERO_MODEL: str = "black-forest-labs/flux-kontext-pro"
    REPLICATE_VIDEO_MODEL: str = "wavespeedai/wan-2.1-i2v-720p"

    VIDEO_ENDCARD_HEADLINE: str = "Sie sind herzlich willkommen"
    VIDEO_ENDCARD_SUBLINE: str = "Genuss, der Lust auf mehr macht"
    VIDEO_LOGO_PATH: str = "static/branding/logo.png"

    REDIS_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
