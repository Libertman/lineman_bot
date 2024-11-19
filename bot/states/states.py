from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from config_data.config import settings


redis = Redis(host=settings.REDIS_HOST)
redis_storage = RedisStorage(redis=redis)

class FSMAdminAddUser(StatesGroup):
    filling_user_info = State()

class FSMAdminAddDeadline(StatesGroup):
    filling_deadline_info = State()
