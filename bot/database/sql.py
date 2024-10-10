from environs import Env
from sqlalchemy import Integer, BigInteger, String, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config_data.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True)

session_marker = async_sessionmaker(engine, expire_on_commit=True)

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(200), nullable=True)
    fullname: Mapped[str] = mapped_column(String(200))
    flag: Mapped[int] = mapped_column(Integer, default=0)


async def insert_new_user(user_id: int, username: str, fullname: str = None):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.id == user_id))
        needed_data = query.scalar()
        if not needed_data:
            new_user = User(id=user_id, username=username, fullname=fullname)
            session.add(new_user)
            await session.commit()

async def update_data(user_id: int, flag: int = 0, username: str = None, fullname: str = None):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.id == user_id))
        needed_data = query.scalar()
        if username:
            needed_data.username = username
        if fullname:
            needed_data.fullname = fullname
        if flag:
            needed_data.flag = 1
        await session.commit()

async def get_user(user_id: int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.id == user_id))
        needed_data = query.scalar()
        if needed_data:
            return needed_data.id, needed_data.username, needed_data.fullname, needed_data.flag
        return None


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# env = Env()
# env.read_env()


# # def dict_factory(cursor, row):
#     save_dict = {}
#     for idx, col in enumerate(cursor.description):
#         save_dict[col[0]] = row[idx]
#     return save_dict

# def add_user(user_id, flag, fullname, username=None):
#     with sqlite3.connect(env('PATH_DATABASE')) as con:
#         con.row_factory = dict_factory
#         con.execute('''
#         CREATE TABLE IF NOT EXISTS users(
#         user_id INTEGER PRIMARY KEY,
#         username TEXT,
#         fullname TEXT,
#         flag INTEGER NOT NULL)''')
#         con.execute("INSERT INTO users "
#                     "(user_id, username, fullname, flag) "
#                     "VALUES (?, ?, ?, ?)",
#                     [user_id, username, fullname, flag])
#         con.commit()

# def update_format_args(sql, parameters: dict):
#     sql += " WHERE " + " AND ".join([
#         f"{item} = ?" for item in parameters
#     ])

#     return sql, list(parameters.values())

# def get_user(**kwargs):
#     with sqlite3.connect(env('PATH_DATABASE')) as con:
#         con.row_factory = dict_factory
#         con.execute('''
#         CREATE TABLE IF NOT EXISTS users(
#         user_id INTEGER PRIMARY KEY,
#         username TEXT,
#         fullname TEXT,
#         flag INTEGER NOT NULL)''')
#         sql = "SELECT * FROM users"
#         sql, parameters = update_format_args(sql, kwargs)
#         return con.execute(sql, parameters).fetchone()

# def get_users(**kwargs):
#     with sqlite3.connect(env('PATH_DATABASE')) as con:
#         con.row_factory = dict_factory
#         sql = "SELECT * FROM users"
#         sql, parameters = update_format_args(sql, kwargs)
#         return con.execute(sql, parameters).fetchall()

# def update_format(sql, parameters: dict):
#     if "XXX" not in sql:
#         sql += " XXX "

#     values = ", ".join([
#         f"{item} = ?" for item in parameters
#     ])
#     sql = sql.replace("XXX", values)

#     return sql, list(parameters.values())

# def update_user(user_id, **kwargs):
#     with sqlite3.connect(env('PATH_DATABASE')) as con:
#         con.row_factory = dict_factory
#         sql = f"UPDATE users SET"
#         sql, parameters = update_format(sql, kwargs)
#         parameters.append(user_id)
#         con.execute(sql + "WHERE user_id = ?", parameters)
#         con.commit()
