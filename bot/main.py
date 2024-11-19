from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import settings
from handlers import user_handlers, admin_handlers
from middlewares.exists_user import ExistsUserMiddleware
from database.sql import init_models, check_deadlines
from states.states import redis_storage
import asyncio
import logging


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')

    logger.info('Starting my bot')
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=redis_storage)

    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.admin_router)

    dp.update.outer_middleware(ExistsUserMiddleware())

    await init_models()

    asyncio.create_task(check_deadlines(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
