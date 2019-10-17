import psycopg2
import config
import logging


exiting = 0

try:
    connection = psycopg2.connect(user=config.db_user,
                                    password=config.db_psw,
                                    host="localhost",
                                    port="5432",
                                    database=config.db_name)
    connection.set_session(autocommit=True)
except Exception as e:
    logging.error("Error while connecting to database")
    logging.error(e)


def finish():
    if connection:
        connection.close()
