from sqlalchemy import Integer, BigInteger, String, ForeignKey, DateTime, select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from config_data.config import settings
from datetime import datetime, timedelta
from lexicon.lexicon_ru import LEXICON_RU
from services.services import translate_to_date
from keyboards.keyboards import check_already_done
import enum
import logging
import asyncio


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')


engine = create_async_engine(settings.DATABASE_URL, echo=True)

session_marker = async_sessionmaker(engine, expire_on_commit=True)

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class DeadlineType(enum.Enum):
    SUBJECT = 'Subjects'
    USER = 'Users'

class User(Base):
    __tablename__ = 'Users'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(200), nullable=True)
    fullname: Mapped[str] = mapped_column(String(200))
    subjects_names: Mapped[ARRAY] = mapped_column(ARRAY(String))

    Deadlines: Mapped[list['Deadline']] = relationship('Deadline', back_populates='Users', cascade='all, delete-orphan')


class Deadline(Base):
    __tablename__ = 'Deadlines'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    date: Mapped[DateTime] = mapped_column(DateTime)
    reminders: Mapped[ARRAY] = mapped_column(ARRAY(Integer))
    deadline_type: Mapped[DeadlineType] = mapped_column()

    user_index: Mapped[int] = mapped_column(BigInteger, ForeignKey('Users.index'))

    Users: Mapped['User'] = relationship('User', back_populates='Deadlines')


class Subject(Base):
    __tablename__ = 'Subjects'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(300))
    date: Mapped[DateTime] = mapped_column(DateTime)
    reminders: Mapped[ARRAY] = mapped_column(ARRAY(Integer))


async def insert_new_user(u_id: int, username: str, fullname: str = None):
    now = datetime.now() + timedelta(hours=3)
    async with session_marker() as session:
        user_query = await session.execute(select(User).filter(User.id == u_id))
        user_data = user_query.scalar()
        if not user_data:
            user_data = User(id=u_id, username=username, fullname=fullname, subjects_names=['Физическая культура', 'Экономическая культура', 'Россия: гос. осн. и мировоззрение', 'Цифровая грамотность', 'Английский язык'])
            session.add(user_data)
        subjects_query = await session.execute(select(Subject).filter(Subject.date > now))
        subjects_data = subjects_query.scalars().all()
        deadline_query = await session.execute(select(Deadline).filter(Deadline.user_index == u_id))
        deadline_data = deadline_query.scalars().first()
        if not deadline_data:
            user_query = await session.execute(select(User).filter(User.id == u_id))
            user_data = user_query.scalar()
            for deadline in subjects_data:
                deadline.reminders = list(filter(lambda x: deadline.date - timedelta(seconds=x) > now, deadline.reminders))
                session.add(Deadline(subject_name=deadline.name, title=deadline.title, date=deadline.date, reminders=deadline.reminders, deadline_type=DeadlineType.SUBJECT, user_index=user_data.index))
        await session.commit()


async def update_data(user_id: int, username: str = None, fullname: str = None):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.id == user_id))
        needed_data = query.scalar()
        if username:
            needed_data.username = username
        if fullname:
            needed_data.fullname = fullname
        await session.commit()


async def get_user(user_id: int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.id == user_id))
        needed_data = query.scalar()
        if needed_data:
            return needed_data.id, needed_data.username, needed_data.fullname
        return None


async def get_user_deadlines(user_id: int):
    async with session_marker() as session:
        user_query = await session.execute(select(User).filter(User.id == user_id))
        user_data = user_query.scalar()
        deadline_query = await session.execute(select(Deadline).filter(Deadline.user_index == user_data.index))
        deadline_data = deadline_query.scalars().all()
        return sorted([{"subject": deadline.subject_name, "title": deadline.title, "deadline": deadline.date} for deadline in deadline_data], key=lambda x: x["deadline"])


async def get_subject_deadlines(subject: str):
    datetime_now = datetime.now() + timedelta(hours=3)
    async with session_marker() as session:
        query = await session.execute(select(Subject).filter(Subject.name == subject, Subject.date > datetime_now))
        needed_data = query.scalars().all()
        return [{"title": deadline.title, "deadline": deadline.date} for deadline in needed_data]


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    initial_data = [
        Subject(title='Аттестация по модулю: Основы теории физической культуры', date=datetime(2024, 10, 7), name='Физическая культура'),
        Subject(title='Аттестация по модулю: Медико, биологические основы физической культуры', date=datetime(2024, 10, 14), name='Физическая культура'),
        Subject(title='Аттестация по модулю: Самостоятельные занятия физическими упражнениями', date=datetime(2024, 10, 25), name='Физическая культура'),
        Subject(title='Аттестация по модулю: Физическая культура в профессиональной деятельности специалиста', date=datetime(2024, 10, 29), name='Физическая культура'),
        Subject(title='Аттестация по модулю: Спорт как социальное явление', date=datetime(2024, 11, 4), name='Физическая культура'),
        Subject(title='Аттестация по модулю: Физическая культура при различных заболеваниях', date=datetime(2024, 11, 6), name='Физическая культура'),
        Subject(title='Промежуточная аттестация', date=datetime(2024, 11, 16), name='Физическая культура'),
        Subject(title='Итоговый тест с прокторингом', date=datetime(2024, 12, 1), name='Физическая культура'),
        Subject(title='Основные экономические категории', date=datetime(2024, 9, 23), name='Экономическая культура'),
        Subject(title='Финансы домашних хозяйств', date=datetime(2024, 9, 30), name='Экономическая культура'),
        Subject(title='Сбережения и инвестиции физических лиц', date=datetime(2024, 10, 7), name='Экономическая культура'),
        Subject(title='Пенсионные сбережения', date=datetime(2024, 10, 14), name='Экономическая культура'),
        Subject(title='Инвестирование на фондовом рынке', date=datetime(2024, 10, 21), name='Экономическая культура'),
        Subject(title='Платежи и расчеты', date=datetime(2024, 10, 28), name='Экономическая культура'),
        Subject(title='Кредиты и займы', date=datetime(2024, 11, 4), name='Экономическая культура'),
        Subject(title='Налогооблажение физических лиц', date=datetime(2024, 11, 11), name='Экономическая культура'),
        Subject(title='Страхование рисков и профессиональной деятельности', date=datetime(2024, 11, 18), name='Экономическая культура'),
        Subject(title='Организационные аспекты индивидуальной предпринимательской деятельности и самозанятости в РФ', date=datetime(2024, 11, 25), name='Экономическая культура'),
        Subject(title='Практическая реализация предпринимательской идеи', date=datetime(2024, 12, 2), name='Экономическая культура'),
        Subject(title='Итоговая аттестация', date=datetime(2024, 12, 9), name='Экономическая культура'),
        Subject(title='\n1. Что такое Россия\n2. Российское государство, цивилизация\n3. Российское мировоззрение и ценности российской цивилизации\n4. Политическое устройство России\n5. Вызовы будущего и развитие страны', date=datetime(2024, 11, 30), reminders=[108000], name='Россия: гос. осн. и мировоззрение'),
        Subject(title='Амнистия', date=datetime(2024, 12, 21), name='Россия: гос. осн. и мировоззрение'),
        Subject(title='Итоговая аттестация', date=datetime(2024, 12, 23), name='Россия: гос. осн. и мировоззрение'),
        Subject(title='\n1. Компьютерные системы и сети\n2. Интернет вещей\n3. Цифровая городская среда\n4. Финансовые технологии\n5. Основы информационной безопасности\n6. Цифровая гигиена\n7. Технологии виртуальной, дополненной и смешанной реальности\n8. Коммуникационная безопасность\n9. Амнистия\n10. Итоговая аттестация', date=datetime(2024, 12, 23), reminders=[108000], name='Цифровая грамотность'),
        Subject(title='Тест по модулю 1', date=datetime(2024, 10, 9), name='Английский язык'),
        Subject(title='Монолог по модулю 1 "Personality"', date=datetime(2024, 10, 16), name='Английский язык'),
        Subject(title='Тест по модулю 2', date=datetime(2024, 10, 23), name='Английский язык'),
        Subject(title='Монолог по модулю 2 "Travel"', date=datetime(2024, 11, 7), name='Английский язык'),
        Subject(title='Тест по модулю 3', date=datetime(2024, 11, 13), name='Английский язык'),
        Subject(title='Монолог по модулю 3 "Work"', date=datetime(2024, 11, 26), name='Английский язык'),
        Subject(title='Тест по модулю 4', date=datetime(2024, 12, 12), name='Английский язык'),
        Subject(title='Монолог по модулю 4 "Language"', date=datetime(2024, 12, 10), name='Английский язык')
    ]

    async with session_marker() as session:
        result = await session.execute(select(Subject).limit(1))
        if not result.scalars().first():
            for deadline in initial_data:
                deadline.reminders = [10800, 21600] + deadline.reminders if deadline.reminders else [10800, 21600]
            session.add_all(initial_data)

            await session.commit()


async def check_deadlines(bot):
    async with session_marker() as session:
        while True:
            now = datetime.now() + timedelta(hours=3)
            query = await session.execute(select(Deadline).order_by(Deadline.date))
            expired_deadlines = []
            for deadline in query.scalars().all():
                if deadline.date < now:
                    await session.execute(delete(Deadline).filter(Deadline.index == deadline.index))
                else:
                    if len(deadline.reminders) == 0:
                        await asyncio.sleep(60)
                        continue
                    if deadline.date - timedelta(seconds=deadline.reminders[-1]) < now:
                        expired_deadlines.append(deadline)
            for deadline in expired_deadlines:
                user_query = await session.execute(select(User).filter(User.index == deadline.user_index))
                users = user_query.scalars().all()
                for user in users:
                    if deadline.deadline_type == DeadlineType.SUBJECT:
                        if deadline.reminders[-1] >= 108000:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['courses_deadlines']['deadline_far_reminder'].format(LEXICON_RU['courses_linkers'][deadline.subject_name]['course'], deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1])), LEXICON_RU['courses_linkers'][deadline.subject_name]['answers']), reply_markup=check_already_done, disable_web_page_preview=True)
                        elif deadline.reminders[-1] >= 21600:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['courses_deadlines']['deadline_common_reminder'].format(LEXICON_RU['courses_linkers'][deadline.subject_name]['course'], deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1])), LEXICON_RU['courses_linkers'][deadline.subject_name]['answers']), reply_markup=check_already_done, disable_web_page_preview=True)
                        else:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['courses_deadlines']['deadline_emergency_reminder'].format(LEXICON_RU['courses_linkers'][deadline.subject_name]['course'], deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1])), LEXICON_RU['courses_linkers'][deadline.subject_name]['answers']), reply_markup=check_already_done, disable_web_page_preview=True)
                    else:
                        if deadline.reminders[-1] >= 108000:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['users_deadlines']['deadline_far_reminder'].format(deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1]))), reply_markup=check_already_done, disable_web_page_preview=True)
                        elif deadline.reminders[-1] >= 7200:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['users_deadlines']['deadline_common_reminder'].format(deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1]))), reply_markup=check_already_done, disable_web_page_preview=True)
                        else:
                            await bot.send_message(chat_id=user.id, text=LEXICON_RU['users_deadlines']['deadline_emergency_reminder'].format(deadline.subject_name, deadline.title, translate_to_date(timedelta(seconds=deadline.reminders[-1]))), reply_markup=check_already_done, disable_web_page_preview=True)
                change_reminders = await session.execute(select(Deadline).filter(Deadline.index == deadline.index))
                need_to_change = change_reminders.scalar()
                need_to_change.reminders = need_to_change.reminders[:-1]
            await session.commit()
            await asyncio.sleep(60)


async def add_subject_deadline_base(data: dict):
    async with session_marker() as session:
        now = datetime.now() + timedelta(hours=3)
        reminders_list = [list(data.values())[7+i:7+i+3] for i in range(0, len(data) - 9, 3)]
        deadline_date = datetime(data['deadline_year'], data['deadline_month'], data['deadline_day'], data['deadline_hour'], data['deadline_minute'])
        common_reminders = list(filter(lambda x: deadline_date - x > now, [timedelta(hours=6), timedelta(hours=3)]))
        reminders = sorted([int(timedelta(days=reminder[0], hours=reminder[1], minutes=reminder[2]).total_seconds()) for reminder in reminders_list] + list(map(lambda x: int(x.total_seconds()), common_reminders)))

        session.add(Subject(name=data['subject_name'], title=data['lesson_name'], date=deadline_date, reminders=reminders))
        users_query = await session.execute(select(User).filter(User.subjects_names.contains([data['subject_name']])))
        users_data = users_query.scalars().all()
        for user in users_data:
            session.add(Deadline(subject_name=data['subject_name'], title=data['lesson_name'], date=deadline_date, reminders=reminders, deadline_type=DeadlineType.SUBJECT, user_index=user.index))
        await session.commit()


async def add_user_base(data: dict):
    now = datetime.now() + timedelta(hours=3)
    async with session_marker() as session:
        session.add(User(id=data['id'] , username=data['username'], fullname=data['fullname'], subjects_names=data['subject_names']))
        deadlines_query = await session.execute(select(Subject).filter(Subject.name.in_(data['subject_names']), Subject.date > now))
        deadlines_data = deadlines_query.scalars().all()
        user_query = await session.execute(select(User).filter(User.id == data['id']))
        user_data = user_query.scalars().first()
        for deadline in deadlines_data:
            deadline.reminders = list(filter(lambda x: deadline.date - timedelta(seconds=x) > now, deadline.reminders))
            session.add(Deadline(subject_name=deadline.name, title=deadline.title, date=deadline.date, reminders=deadline.reminders, deadline_type=DeadlineType.SUBJECT, user_index=user_data.index))
        await session.commit()


async def delete_completed_task(title: str, user_id: int, subject_name: str = None):
    now = datetime.now() + timedelta(hours=3)
    async with session_marker() as session:
        user_query = await session.execute(select(User).filter(User.id == user_id))
        user_data = user_query.scalar()
        if subject_name:
            deadline_query = await session.execute(select(Deadline).filter(Deadline.subject_name == subject_name, Deadline.title == title, Deadline.user_index == user_data.index))
        else:
            deadline_query = await session.execute(select(Deadline).filter(Deadline.title == title, Deadline.user_index == user_data.index, Deadline.subject_name.is_(None)))
        deadline_data = deadline_query.scalar()
        if not deadline_data or deadline_data.date < now:
            return False
        await session.execute(delete(Deadline).filter(Deadline.index == deadline_data.index))
        await session.commit()
        return True
