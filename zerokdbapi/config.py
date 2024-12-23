from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class Settings(BaseSettings):
    pinata_api_key: str
    api_host: str
    aptos_table_sequence_contract: str
    aptos_private_key: str

    class Config:
        extra = "allow"
        env_file = find_dotenv()


settings = Settings()
