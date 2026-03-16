from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    jwt_issuer: str = "lexclaw"
    jwt_audience: str = "lexclaw-api"
    jwt_secret: str = "change-me"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 7
    license_token_ttl_days: int = 30
    billing_webhook_secret: str = "dev-billing-webhook-secret"


settings = Settings()
