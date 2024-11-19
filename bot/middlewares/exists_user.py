from aiogram import BaseMiddleware
from database.sql import get_user, insert_new_user, update_data
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')


class ExistsUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.prefix = "key_prefix"
        super(ExistsUserMiddleware, self).__init__()

    async def __call__(self, handler, event, data: dict):
        if data['event_context'].chat.type == 'private':
            this_user = data['event_from_user']

            if this_user.is_bot:
                return handler(event, data)

            user = await get_user(user_id=this_user.id)

            username = this_user.username
            fullname = this_user.full_name

            if username is None:
                username = ""
        else:
            this_user = data['event_context'].chat
            user = await get_user(user_id=this_user.id)
            username = None
            fullname = this_user.title
        user_id = this_user.id

        if user is None:
            await insert_new_user(user_id, username, fullname)
            return await handler(event, data)
        elif 'event_from_user' in data and (username != user[1] or fullname != user[2]):
            await update_data(user_id, username=username, fullname=fullname)
        return await handler(event, data)