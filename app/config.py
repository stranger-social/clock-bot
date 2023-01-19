from pydantic import BaseSettings

class Settings(BaseSettings):
    quiet: bool = True
    logging_level: str = "INFO"
    mastodon_base_url: str
    mastodon_domain: str
    mastodon_access_token: str
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    tz: str

    class Config:
        env_file = ".env"

settings = Settings()