#!/usr/bin/env python3

""" basic rss reader """

from configparser import ConfigParser
import subprocess

import psycopg2
from psycopg2 import sql
import feedparser

def read_config(filename, section):
    """ Read database configuration from file
    Args:
        filename (str): file containing the database specifications
        section (str): which section to take
    Returns:
        rss_db (dict): configuration parameters of database
    """
    config_parser = ConfigParser()
    config_parser.read(filename)
    rss_db = {}
    if config_parser.has_section(section):
        parameters = config_parser.items(section)
        for key, value in parameters:
            rss_db[key] = value
    else:
        raise Exception('Section {0} not found in {1} file'.format(section, filename))
    return rss_db



def create_new_table(tablename, connection_to_db, cursor):
    """ create a new table in the database when a new feed is added """
    data = (tablename, )
    cursor.execute(
        sql.SQL(
            "CREATE TABLE IF NOT EXISTS {} (title TEXT, date TEXT)")
        .format(sql.Identifier(tablename))
    ) 
    connection_to_db.commit()


def insert_entry(table, title, date, connection_to_db, cursor):
    """ insert an entry into a table """
    sql_instruction = "INSERT INTO {} VALUES (%s, %s)"
    cursor.execute(
        sql.SQL(sql_instruction).format(
            sql.Identifier(table)),
        [title,  date]
    )
    connection_to_db.commit()


def is_entry_in_db(title, date, table, cursor):
    """ Check if article has an enty in database already """
    sql_query = "SELECT * FROM {} WHERE title=%s AND date=%s"
    cursor.execute(
        sql.SQL(sql_query).format(
            sql.Identifier(table)),
        [title, date]
    )
    if not cursor.fetchall():
        return False
    return True
 

def send_notification(title, url):
    """ send notification to user using notify-send """
    subprocess.call(["notify-send", title, "New article:\n {}".format(url)])


def read_feed(feed_url, table, config_file, section):
    """ Read rss feed of a webpage
    Args:
        feed_url (str): weblink of rss feed
        table (str): name of table to store the articles in
        config_file: name of file containing the configuration of used database
        section: section of configuration to use
    """
    all_articles = feedparser.parse(feed_url)["entries"]
    connection_to_db = None
    try:
        config_parameters = read_config(config_file, section)
        connection_to_db = psycopg2.connect(**config_parameters)
        cursor = connection_to_db.cursor()
        create_new_table(table, connection_to_db, cursor)
        for article in all_articles:
            if is_entry_in_db(article["title"], article["published"], "magazine", cursor):
                continue
            insert_entry("magazine", article["title"], article["published"], connection_to_db,  cursor)
            send_notification(article["title"], article["link"])
    except (Exception, psycopg2.DataError) as error:
        print(error)
    finally:
        if connection_to_db is not None:
            connection_to_db.close()



if __name__ == "__main__":
    CONFIG_FiLE = "rss_db.ini"
    SECTION = "postgresql"
    URL = "https://fedoramagazine.org/feed/"
    read_feed(URL, "magazine", CONFIG_FiLE, SECTION)
