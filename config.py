from pydantic import validator, Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database settings
    database_url: str = Field(..., env='DATABASE_URL')
    database_host: Optional[str] = Field(None, env='DATABASE_HOST')
    database_port: int = Field(5432, env='DATABASE_PORT')
    database_name: str = Field('kitchen_manager', env='DATABASE_NAME')
    database_user: str = Field('postgres', env='DATABASE_USER')
    database_password: str = Field(..., env='DATABASE_PASSWORD')
    
    # Connection pool settings
    pool_size: int = Field(20, env='DB_POOL_SIZE')
    max_overflow: int = Field(30, env='DB_MAX_OVERFLOW')
    pool_timeout: int = Field(30, env='DB_POOL_TIMEOUT')
    pool_recycle: int = Field(3600, env='DB_POOL_RECYCLE')
    pool_pre_ping: bool = Field(True, env='DB_POOL_PRE_PING')
    
    # AWS RDS specific settings
    connect_timeout: int = Field(10, env='DB_CONNECT_TIMEOUT')
    read_timeout: int = Field(30, env='DB_READ_TIMEOUT')
    db_ssl_mode: str = Field('require', env='DB_SSL_MODE')
    application_name: str = Field('kitchen_manager_api', env='DB_APPLICATION_NAME')
    statement_timeout: int = Field(30000, env='DB_STATEMENT_TIMEOUT')
    idle_in_transaction_session_timeout: int = Field(300000, env='DB_IDLE_TIMEOUT')
    
    # Security settings
    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field('HS256', env='ALGORITHM')
    access_token_expire_minutes: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_days: int = Field(7, env='REFRESH_TOKEN_EXPIRE_DAYS')
    
    # CORS settings
    cors_origins: str = Field('http://localhost:3000', env='CORS_ORIGINS')
    cors_allow_credentials: bool = Field(True, env='CORS_ALLOW_CREDENTIALS')
    
    # Rate limiting
    rate_limit_per_minute: int = Field(100, env='RATE_LIMIT_PER_MINUTE')
    rate_limit_burst: int = Field(20, env='RATE_LIMIT_BURST')
    
    # Environment
    environment: str = Field('development', env='ENVIRONMENT')
    debug: bool = Field(False, env='DEBUG')
    
    # API settings
    api_v1_str: str = Field('/api/v1', env='API_V1_STR')
    project_name: str = Field('Home Kitchen Manager API', env='PROJECT_NAME')
    version: str = Field('1.0.0', env='VERSION')
    
    # Logging
    log_level: str = Field('INFO', env='LOG_LEVEL')
    log_format: str = Field('json', env='LOG_FORMAT')
    
    # Pagination
    default_page_size: int = Field(50, env='DEFAULT_PAGE_SIZE')
    max_page_size: int = Field(1000, env='MAX_PAGE_SIZE')
    
    # Redis
    redis_url: Optional[str] = Field(None, env='REDIS_URL')
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('DATABASE_URL is required')
        if not v.startswith('postgresql://'):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @validator('pool_size')
    def validate_pool_size(cls, v):
        if v < 5 or v > 100:
            raise ValueError('Pool size must be between 5 and 100')
        return v
    
    @validator('max_overflow')
    def validate_max_overflow(cls, v):
        if v < 0 or v > 200:
            raise ValueError('Max overflow must be between 0 and 200')
        return v
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string to list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        return self.cors_origins if isinstance(self.cors_origins, list) else [self.cors_origins]
    
    class Config:
        env_file = '.env'
        case_sensitive = False
        extra = 'ignore'  # Ignore extra fields from environment

# Global settings instance
settings = Settings()

# Backward compatibility exports
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
DATABASE_URL = settings.database_url