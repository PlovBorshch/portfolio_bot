import os
from dotenv import load_dotenv

# Загружаем переменные из .env в систему
load_dotenv()

# Достаем их через os.getenv
TOKEN = os.getenv("TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))