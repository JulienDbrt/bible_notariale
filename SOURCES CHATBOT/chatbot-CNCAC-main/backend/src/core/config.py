from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List
import re

def parse_file_size(size_str: str) -> int:
    """Parse file size string like '50MB' to bytes"""
    if size_str.isdigit():
        return int(size_str)

    size_str = size_str.upper()
    match = re.match(r'^(\d+)(KB|MB|GB)$', size_str)
    if not match:
        return 52428800  # Default 50MB

    size, unit = match.groups()
    size = int(size)

    multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    return size * multipliers.get(unit, 1)

class Settings(BaseSettings):
    # Database
    supabase_url: str = Field(default="http://supabase:54321")
    supabase_key: str = Field(default="")

    @field_validator('supabase_url')
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v

    # File upload
    upload_dir: str = Field(default="/app/uploads")
    max_file_size_str: str = Field(default="50MB", alias="MAX_FILE_SIZE")
    allowed_extensions: str = Field(default="pdf,docx,txt,md,pptx,xlsx")

    @property
    def max_file_size(self) -> int:
        return parse_file_size(self.max_file_size_str)

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    # Cognee AI
    cognee_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)

    # Embedding Configuration (from environment variables)
    embedding_model: Optional[str] = Field(default=None)
    embedding_dimensions: Optional[int] = Field(default=None)

    # Minio Configuration
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket_name: str = Field(default="training-docs")
    minio_secure: bool = Field(default=False)

    @field_validator('minio_secure', mode='before')
    @classmethod
    def parse_bool(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == 'true'
        return False

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == 'true'
        return False

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # Ignore extra fields from environment
        "populate_by_name": True  # Allow both field name and alias
    }

settings = Settings()
