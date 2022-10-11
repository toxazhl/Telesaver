from pydantic import BaseModel, BaseSettings, PostgresDsn, RedisDsn, validator


class Bot(BaseModel):
    token: str
    fsm_storage: str
    session_name: str

    @validator("fsm_storage")
    def validate_fsm_storage(cls, v):
        if v not in ("memory", "redis"):
            raise ValueError(
                "Incorrect 'fsm_storage' value. Must be one of: memory, redis"
            )
        return v


class Client(BaseModel):
    api_id: int | str
    api_hash: str
    session_name: str


class Storage(BaseModel):
    redis_dsn: None | RedisDsn = None
    postgres_dsn: PostgresDsn


class Path(BaseModel):
    bot: None | str = None


class Webhook(BaseModel):
    enable: bool
    domain: None | str = None
    path: Path


class Webapp(BaseModel):
    host: str
    port: int


class Config(BaseSettings):
    bot: Bot
    client: Client
    storage: Storage
    webhook: Webhook
    webapp: Webapp

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
