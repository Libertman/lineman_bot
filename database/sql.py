from environs import Env
import sqlite3


env = Env()
env.read_env()


def dict_factory(cursor, row):
    save_dict = {}
    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]
    return save_dict

def add_user(user_id, flag, fullname, username=None):
    with sqlite3.connect(env('PATH_DATABASE')) as con:
        con.row_factory = dict_factory
        con.execute('''
        CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        fullname TEXT,
        flag INTEGER NOT NULL)''')
        con.execute("INSERT INTO users "
                    "(user_id, username, fullname, flag) "
                    "VALUES (?, ?, ?, ?)",
                    [user_id, username, fullname, flag])
        con.commit()

def update_format_args(sql, parameters: dict):
    sql += " WHERE " + " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())

def get_user(**kwargs):
    with sqlite3.connect(env('PATH_DATABASE')) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()

def get_users(**kwargs):
    with sqlite3.connect(env('PATH_DATABASE')) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()

def update_format(sql, parameters: dict):
    if "XXX" not in sql:
        sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())

def update_user(user_id, **kwargs):
    with sqlite3.connect(env('PATH_DATABASE')) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE users SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        con.execute(sql + "WHERE user_id = ?", parameters)
        con.commit()
