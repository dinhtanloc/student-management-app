
import os
import yaml
from dotenv import load_dotenv, find_dotenv
from pyprojroot import here
from sentence_transformers import SentenceTransformer

load_dotenv(find_dotenv())

with open(here("config/project_config.yml")) as cfg:
    app_config = yaml.load(cfg, Loader=yaml.FullLoader)


class LoadProjectConfig:
    def __init__(self) -> None:
        #keys project
        self.djangoprj = os.getenv('DJANGO_KEYS')
        # database settings
        self.dbname=os.getenv('DB_name')
        self.dbuser=os.getenv('DB_user')
        self.dbpassword=os.getenv('DB_password')
        self.dbport=os.getenv('DB_port')
        #chatbot database settings
        self.postgrest_dbms = os.getenv('POSTGRESQL_DBMS_KEY')
        self.mongodb_uri = os.getenv('MONGODB_URL')


     