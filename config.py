from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration settings
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
DATABASE_URL = os.environ.get('DATABASE_URL')