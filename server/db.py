import os
import sqlite3
from contextlib import contextmanager
import logging

db_path = os.path.join(os.path.dirname(__file__), 'checkers.db')


@contextmanager
def cursor(conn):
    c = conn.cursor()
    try:
        yield c
    except Exception as e:
        logging.error(f'An error occurred during execution db query: {e}')
    else:
        conn.commit()
    finally:
        c.close()


def create_schema(conn):
    create_users = """
        create table user
        (
            id   integer primary key autoincrement,
            name varchar(20) unique,
            password varchar(50)
        )
    """

    create_games = """
        create table game
        (
            id integer primary key autoincrement,
            user1 integer,
            user2 integer,
            winner boolean,
            current_step integer,
            foreign key (user1) references user(id),
            foreign key (user2) references user(id),
            foreign key (current_step) references user(id)
        )
    """

    with cursor(conn) as c:
        c.execute(create_users)
        c.execute(create_games)


def startup():
    if not os.path.exists(db_path):
        create_schema(sqlite3.connect(db_path))


def get_connection():
    return sqlite3.connect(db_path)


def create_user(name, password):
    with cursor(get_connection()) as c:
        c.execute("""insert into user (name, password) values (?, ?)""", (name, password))


def select_user(name, password):
    with cursor(get_connection()) as c:
        return c.execute("""select name from user where name = ? and password = ?""", (name, password)).fetchone()


def select_user_by_name(name):
    with cursor(get_connection()) as c:
        return c.execute("""select name from user where name = ?""", (name, )).fetchone()
