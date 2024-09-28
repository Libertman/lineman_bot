from aiogram import BaseMiddleware
from aiogram.types import Update
from database.sql import get_user, add_user, update_user
from aiogram.types import Message


class ExistsUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.prefix = "key_prefix"
        super(ExistsUserMiddleware, self).__init__()

    def __call__(self, handler, event, data: dict):
        this_user = data['event_from_user']

        if this_user.is_bot:
            return handler(event, data)

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
        return handler(event, data)