from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    AUTO_UPGRADE_TAP: bool = True
    MAX_TAP_LEVEL: int = 5
    AUTO_UPGRADE_ATTEMPTS: bool = True
    MAX_ATTEMPTS_LEVEL: int = 5

    RANDOM_SLEEP: list[int] = [15, 30]
    RANDOM_TAPS_COUNT: list[int] = [100, 200]
    SLEEP_BY_MIN_ATTEMPT: list[int] = [3600, 7200]
    LUCK_AMOUNT: int = 200000

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()
