from aiogram import BaseMiddleware
from aiogram.types import Message
from database.sql import get_user, update_data
from states.states import FSMRegistrationUser
from keyboards.keyboards import generate_choice_subjects
from services.services import auto_delete_message
import logging
import time


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
            if ((event.message and event.message.text not in ('/start', '🙏🏻ПОМОГИТЕ🙏🏻')) or event.callback_query) and not(await data['state'].get_state() == FSMRegistrationUser.waiting_for_subjects.state):
                await data['state'].set_state(FSMRegistrationUser.waiting_for_subjects)
                if not (await data['state'].get_data()).get('last_interaction'):
                    bot_message = await data['bot'].send_message(chat_id=data['event_context'].chat.id, text='📝Вам необходимо пройти небольшую регистрацию📝\n\n📚Выберите предметы, по которым вы хотите получать напоминания о дедлайнах', reply_markup=generate_choice_subjects([]))
                    await data['state'].update_data(selected_subjects=[], message_id=bot_message.message_id, last_interaction=int(time.time()))
                    await auto_delete_message(data['bot'], user_id, bot_message.message_id, data['state'], 300)
                    return
            return await handler(event, data)
        elif 'event_from_user' in data and (username != user['username'] or fullname != user['fullname']):
            await update_data(user_id, username=username, fullname=fullname)
        return await handler(event, data)
