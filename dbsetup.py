import sqlite3
from sqlite3 import Error
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    googleid = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'googleid': self.googleid,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_category(conn, category):
    """
    Create a new category
    :param conn:
    :param category:
    :return:
    """
    sql = ''' INSERT INTO category(name,description)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, category)
    return cur.lastrowid


def create_user(conn, user):
    """
    Create a new user
    :param conn:
    :param user:
    :return:
    """
    sql = ''' INSERT INTO user(name,googleid)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    return cur.lastrowid


def create_item(conn, item):
    """
    Create a new item
    :param conn:
    :param item:
    :return:
    """
    sql = ''' INSERT INTO item(name,description,category_id,user_id)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    return cur.lastrowid


def main():
    database = r"catalog.db"

    sql_create_user_table = """ CREATE TABLE IF NOT EXISTS user (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        googleid text
                                    ); """

    sql_create_category_table = """CREATE TABLE IF NOT EXISTS category (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    description text
                                );"""

    sql_create_item_table = """CREATE TABLE IF NOT EXISTS item (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    description text,
                                    category_id integer,
                                    user_id integer,
                                    FOREIGN KEY (category_id)
                                     REFERENCES category (id),
                                    FOREIGN KEY (user_id) REFERENCES user (id)
                                );"""

    category_1 = ('category 1', 'this is the first category')
    category_2 = ('category 2', 'this is the second category')
    category_3 = ('category 3', 'this is the third category')
    category_4 = ('category 4', 'this is the fouth category')

    # user_1 = ('Nicholas Ratliff', 'g1234')

    item_1 = ('item 1', 'this is item 1', 1, 1)
    item_2 = ('item 2', 'this is item 2', 1, 1)
    item_3 = ('item 3', 'this is item 3', 2, 1)
    item_4 = ('item 4', 'this is item 4', 2, 1)
    item_5 = ('item 5', 'this is item 5', 3, 1)
    item_6 = ('item 6', 'this is item 6', 3, 1)
    item_7 = ('item 7', 'this is item 7', 3, 1)
    item_8 = ('item 8', 'this is item 8', 3, 1)
    item_9 = ('item 9', 'this is item 9', 4, 1)
    item_10 = ('item 10', 'this is item 10', 4, 1)
    item_11 = ('item 11', 'this is item 11', 4, 1)
    item_12 = ('item 12', 'this is item 12', 4, 1)

    # create a database connection
    conn = create_connection(database)
    with conn:
        # create tables
        # if conn is not None:
        # create user table
        create_table(conn, sql_create_user_table)

        # create category table
        create_table(conn, sql_create_category_table)

        # create item table
        create_table(conn, sql_create_item_table)

        # create new category's
        create_category(conn, category_1)
        create_category(conn, category_2)
        create_category(conn, category_3)
        create_category(conn, category_4)

        # create user
        # create_user(conn, user_1)

        # create items
        create_item(conn, item_1)
        create_item(conn, item_2)
        create_item(conn, item_3)
        create_item(conn, item_4)
        create_item(conn, item_5)
        create_item(conn, item_6)
        create_item(conn, item_7)
        create_item(conn, item_8)
        create_item(conn, item_9)
        create_item(conn, item_10)
        create_item(conn, item_11)
        create_item(conn, item_12)

    # else:
    #    print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
