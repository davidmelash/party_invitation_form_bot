from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from aiogram_dialog import DialogRegistry

from data import config
from utils.connector import Connector
from utils.db_api.database import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage() if you don't wont to use redis then use MemoryStorage

storage = RedisStorage2()
dp = Dispatcher(bot, storage=storage)
db = Database()
our_sheet = Connector()
registry = DialogRegistry(dp)