import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # take environment variables from .env.

# ============================
# Environment Constants
# ============================
ORIGINS=os.environ.get("ORIGINS", "*").split(",") # for CORS, default is all origins
BASEDIR_APP=os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH=os.environ.get("DATABASE_PATH")
SECRET_KEY=os.environ.get("SECRET_KEY") 
ALGORITHM=os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30) # Default to 30 minutes if not set
COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true" # should be True in production with HTTPS
COOKIE_DOMAIN=os.environ.get("COOKIE_DOMAIN", "localhost") # should be set to the domain of the app in production
SQLALCHEMY_DATABASE_URL=os.environ.get("SQLALCHEMY_DATABASE_URL")
REDIS_URL=os.environ.get("REDIS_URL", "localhost")  # Default to localhost if not set
REDIS_PASSWORD=os.environ.get("REDIS_PASSWORD", "")  # Default to empty string if not set
REDIS_PORT=os.environ.get("REDIS_PORT")
REDIS_EX=os.environ.get("REDIS_EX", 600)  # Default to 600 seconds if not set