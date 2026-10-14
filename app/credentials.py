from pydantic import BaseModel, Field

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")


settings = Settings()