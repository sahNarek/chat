import os
from pydantic_settings import BaseSettings
from dotenv import dotenv_values

env_vars = {
    **dotenv_values(".env"),
    **os.environ
}


class Config(BaseSettings):
    TYPE: str = "standard"
    PORT: int = env_vars.get("PORT", 8000)
    DATABASE_URL: str = env_vars.get("DATABASE_URL","")
    MODEL_NAME: str = env_vars.get("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    JWT_SECRET_KEY: str = env_vars.get("JWT_SECRET_KEY","")
    USER_ROLE: str = env_vars.get("STANDARD_USER_ROLE", "USER")
    ENDPOINT: str = env_vars.get("STANDARD_ENDPOINT", "/completions/standard")
    QUESTIONS_LIMIT: int = env_vars.get("STANDARD_QUESTIONS_LIMIT", 4)


class PremiumConfig(Config):
    TYPE: str = "premium"
    PORT: int = env_vars.get("PREMIUM_PORT", 8001)
    MODEL_NAME: str = env_vars.get("PREMIUM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    USER_ROLE: str = env_vars.get("PREMIUM_USER_ACCESS_ROLE", "PREMIUM_USER")
    ENDPOINT: str = env_vars.get("PREMIUM_ENDPOINT", "/completions/premium")
    QUESTIONS_LIMIT: int = env_vars.get("PREMIUM_QUESTIONS_LIMIT", 20)


def get_config():
    """Get the configuration object

    Args:
        config_type (str, optional): Configuration type for loading. Defaults to "".

    Returns:
        _type_: _description_
    """
    server_mode = env_vars.get("SERVER_MODE", "standard")
    if server_mode == "standard":
        return Config()
    elif server_mode == "premium":
        return PremiumConfig()
    else:
        raise ValueError(f"Invalid server mode: {server_mode}")



app_config = get_config()
