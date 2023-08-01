from environs import Env

env = Env()
env.read_env()

HONEYBOOK_EMAIL = env.str('HB_EMAIL')
HONEYBOOK_PASSWORD = env.str('HB_PASSWORD')

DB_USER = env.str('DB_USER')
DB_PASSWORD = env.str('DB_PASSWORD')
DB_DATABASE = env.str('DB_DATABASE')
DB_HOST = env.str('DB_HOST')

BOT_TOKEN = env.str('BOT_TOKEN')
CHAT_IDS = env.list('CHAT_IDS')
