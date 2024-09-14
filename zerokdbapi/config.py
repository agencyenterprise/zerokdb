from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    pinata_api_key: str
    pinata_secret_api_key: str
    provider_url: str
    contract_address: str
    abi_path: str
    from_address: str
    private_key: str

    class Config:
        env_file = ".env"

settings = Settings()
