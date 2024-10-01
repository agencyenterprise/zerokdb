from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class Settings(BaseSettings):
    pinata_api_key: str
    provider_url: str
    contract_address: str
    abi_path: str
    from_address: str
    private_key: str
    api_host: str

    class Config:
        extra = "allow"
        env_file = find_dotenv()


settings = Settings()
