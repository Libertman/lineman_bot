from aiogram import BaseMiddleware
from aiogram.types import Update
from database.sql import get_user, add_user, update_user


class ExistsUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.prefix = "key_prefix"
        super(ExistsUserMiddleware, self).__init__()

    async def on_process_update(self, update: Update, data: dict):
        if "message" in update:
            this_user = update.message.from_user
        elif "callback_query" in update:
            this_user = update.callback_query.from_user
        else:
            return

        if this_user.is_bot:
            return

        user = get_user(user_id=this_user.id)

        user_id = this_user.id
        username = this_user.username
        fullname = this_user.full_name

        if username is None:
            username = ""

        if user is None:
            add_user(user_id, username, fullname)
        elif username != user['username'] or fullname != user['fullname']:
            update_user(user['user_id'], username=username, fullname=fullname)