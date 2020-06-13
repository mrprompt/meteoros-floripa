#!/usr/bin/env python3
# -*- coding: utf8 -*-
import os
import argparse
import re
import sqlite3
from typing import List
from xml.dom import minidom

PATH = os.path.dirname(__file__)
PATH_OF_ANALYZERS = "{}/../_data/".format(PATH)


def cleanup_dir(directory: str, extension: str) -> bool:
    """
    Remove posts and captures before recreate then.

    :param directory: Name of directory to cleanup md files.
    :returns bool
    """
    file_list = [f for f in os.listdir(directory) if f.endswith(extension)]

    for f in file_list:
        file_to_delete = os.path.join(directory, f)

        os.remove(file_to_delete)

    return True


def organize_captures(stations_captures: List) -> List:
    """
    Organize captures to be inserted into database with
    correct params organized into a tuple.

    :param stations_captures: The array all captures
    :returns List
    """
    captures_organized = []

    for capture in stations_captures:
        base = re.findall("\w{3}\d{1,2}.+", capture)
        capture_spliced = base[0].split(os.sep)
        station = capture_spliced[0]
        capture_date = capture_spliced[3]
        post = (capture_date, station, capture)

        captures_organized.append(post)

    return captures_organized


def populate_tables(connection: object, captures_list: List) -> bool:
    """
    Insert posts into table

    :param connection: The database connection
    :param captures_list: Array of posts
    :returns: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    CREATE TABLE IF NOT EXISTS captures (
        id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
        night_start DATE NOT NULL,
        station VARCHAR(20) NOT NULL,
        files TEXT
    );
    """)

    connection_cursor.executemany("""
    INSERT INTO captures (night_start, station, files)
    VALUES (?, ?, ?)
    """, captures_list)

    connection.commit()

    return True


def generate_collections(connection: object) -> bool:
    """
    Generate captures collections from every station captures.

    :param connection: The database connection
    :return: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    SELECT night_start, station
    FROM captures
    GROUP BY night_start, station
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        station = str(data[1])
        capture_filename = PATH_OF_ANALYZERS + "analyzers.yaml"

        connection_cursor.execute("""
            SELECT id, night_start, station, files
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            file = capture[3]


            try:
                xmldoc = minidom.parse(file)
                itemlist = xmldoc.getElementsByTagName('ua2_object')
                classe = itemlist[0].attributes['class'].value
            except IndexError:
                classe = "__none__"
            except Exception:
                classe = "__none__"

            base = re.findall("\w{3}\d{1,2}.+", file)
            capture_spliced = base[0].split('/')
            capture_base_filename = capture_spliced[-1]

            filehandle = open(capture_filename, "a")
            filehandle.write("{}:\n".format(base[0].replace('A.XML', 'P.jpg')))
            filehandle.write("  station: {}\n".format(station))
            filehandle.write("  class: {}\n".format(classe))
            filehandle.close()

    return True


def get_matching_analyzers(captures_dir: list):
    import glob

    result = []

    for directory in captures_dir:
        files = glob.glob("{}/**/*A.XML".format(directory), recursive=True)

        result.extend(files)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process captures files and create posts.')
    parser.add_argument('captures_dir', metavar='captures', type=str, nargs='+', help='captures directory input')

    args = parser.parse_args()

    print("- Cleaning {}".format(PATH_OF_ANALYZERS))
    cleanup_dir(PATH_OF_ANALYZERS, ".yaml")

    print("- Reading analyzer files from {}".format(args.captures_dir))
    analyzers = get_matching_analyzers(args.captures_dir)

    print("- Organizing captures")
    posts = organize_captures(analyzers)

    print("- Connecting to database")
    conn = sqlite3.connect(':memory:')

    print("- Creating temporary table and populating...")
    populate_tables(conn, posts)

    print("- Creating data collections")
    generate_collections(conn)

    print("- Closing database connection")
    conn.close()

    print("- Done :)")
