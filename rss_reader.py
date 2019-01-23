#!/usr/bin/env python3

""" A (very) basic rss reader implementation  using a postgresql database

This script accesses a changable rss feed and stores the key identifiers of an
article (title, date of publication) in a postgresql database.
On each call, the user is informed of new articles via a desktop notification.

This tool requires an installation of postgresql on your machine as well as the
externel python modules:
    * psycopg2
    * feedparser

The original idea (and an implemantion of the idea using email notification and
a sqlite database ) is accessible on
https://fedoramagazine.org/never-miss-magazines-article-build-rss-notification-system/
and on github:
https://github.com/cverna/rss_feed_notifier
"""

from configparser import ConfigParser
import subprocess
import argparse
import logging

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
        [title, date]
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
            insert_entry(
                "magazine",
                article["title"],
                article["published"],
                connection_to_db,
                cursor
            )
            send_notification(article["title"], article["link"])
    except (Exception, psycopg2.DataError) as dataerror:
        logging.exception(dataerror)
    finally:
        if connection_to_db is not None:
            connection_to_db.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='basic rss feed reader',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="rss_db.ini",
        help="configuration file of the used database"
    )
    parser.add_argument(
        "--section",
        type=str,
        default="postgresql",
        help="section of the config file to use"
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default="https://fedoramagazine.org/feed/",
        help="weburl to access feed"
    )
    parser.add_argument(
        "-t",
        "--table",
        type=str,
        default="magazine",
        help="table in the database to store key information of old articles in"
    )
    args = parser.parse_args()
    read_feed(
        args.url,
        args.table,
        args.config,
        args.section
    )
