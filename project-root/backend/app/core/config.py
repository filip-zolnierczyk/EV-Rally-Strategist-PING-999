import os
from dotenv import load_dotenv

load_dotenv()

OPENCHARGEMAP_API_KEY = os.getenv("OPENCHARGEMAP_API_KEY")
OPENCHARGEMAP_URL = os.getenv("OPENCHARGEMAP_URL")