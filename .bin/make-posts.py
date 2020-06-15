#!/usr/bin/env python3
# -*- coding: utf8 -*-
import argparse
import datetime
import glob
import os
import re
import sqlite3
import subprocess
from xml.dom import minidom
from typing import List


PATH = os.path.dirname(__file__)
PATH_OF_SITE_POSTS = "{}/../_posts/".format(PATH)
PATH_OF_SITE_CAPTURES = "{}/../_captures/".format(PATH)
PATH_OF_WATCH_CAPTURES = "{}/../watch/".format(PATH)
PATH_OF_ANALYZERS = "{}/../_data/".format(PATH)


def populate_tables(connection: object, captures_list: List):
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
        files TEXT,
        files_full_path TEXT
    );
    """)

    connection_cursor.executemany("""
    INSERT INTO captures (night_start, station, files, files_full_path)
    VALUES (?, ?, ?, ?)
    """, captures_list)

    connection.commit()


def organize_captures(stations_captures):
    """
    Organize captures to be inserted into database with
    correct params organized into a tuple.

    :param stations_captures: The array all captures
    :returns List
    """
    captures_organized = []
    er_filter = "\w{3}\d{1,2}.+P.jpg$"

    for capture in stations_captures:
        base = re.findall(er_filter, capture)
        capture_spliced = base[0].split('/')
        station = capture_spliced[0]
        capture_date = capture_spliced[3]
        post = (capture_date, station, base[0], capture)

        captures_organized.append(post)

    populate_tables(connection, captures_organized)


def generate_captures(connection: object) -> bool:
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
        capture_filename = PATH_OF_SITE_CAPTURES + "{}_{}.md".format(station, night_start)

        connection_cursor.execute("""
            SELECT id, night_start, station, files
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            file = capture[3]

            capture_spliced = file.split('/')
            capture_base_filename = capture_spliced[-1]
            capture_data_spliced = capture_base_filename.split('_')

            capture_date = capture_data_spliced[0]
            capture_day = capture_date[7:9]
            capture_month = capture_date[5:7]
            capture_year = capture_date[1:5]

            capture_time = capture_data_spliced[1]
            capture_hour = capture_time[0:2]
            capture_minute = capture_time[2:4]
            capture_second = capture_time[4:6]

            if not os.path.exists(capture_filename):
                filehandle = open(capture_filename, "w+")
                filehandle.write("---\n")
                filehandle.write("layout: capture\n")
                filehandle.write("label: {}\n".format(night_start))
                filehandle.write("station: {}\n".format(station))
                filehandle.write("date: {}-{}-{} {}:{}:{}\n".format(capture_year, capture_month, capture_day, capture_hour, capture_minute, capture_second))
                filehandle.write("preview: {}\n".format(file))
                filehandle.write("capturas:\n")
            else:
                filehandle = open(capture_filename, "a")

            filehandle.write("  - imagem: {}\n".format(file))
            filehandle.close()

        filehandle = open(capture_filename, "a")
        filehandle.write("---\n")
        filehandle.close()

    return True


def generate_posts(connection: object) -> bool:
    """
    Generate captures collections and pages from every station captures.

    :param connection: The database connection
    :return: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    SELECT night_start, files
    FROM captures
    GROUP BY night_start
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        day = str(night_start[6:8])
        month = str(night_start[4:6])
        year = str(night_start[0:4])
        file_preview = str(data[1])
        post_filename = PATH_OF_SITE_POSTS + "{}-{}-{}-captures.md".format(year, month, day)

        filehandle = open(post_filename, "w+")
        filehandle.write("---\n")
        filehandle.write("layout: post\n")
        filehandle.write("title: {}/{}/{}\n".format(day, month, year))
        filehandle.write("date: {}-{}-{} 10:00:00\n".format(year, month, day))
        filehandle.write("preview: {}\n".format(file_preview))
        filehandle.write("---\n")
        filehandle.close()

    return True


def generate_watches(connection: object) -> bool:
    """
    Generate watch page for each collection item.

    :param connection: The database connection
    :return: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    SELECT night_start, station, files
    FROM captures
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        station = str(data[1])
        file = str(data[2])

        capture_spliced = file.split('/')
        capture_base_filename = capture_spliced[-1]
        capture_base_filename_spliced = capture_base_filename.split('_')

        day = capture_base_filename_spliced[0][7:9]
        month = capture_base_filename_spliced[0][5:7]
        year = capture_base_filename_spliced[0][1:5]
        hour = capture_base_filename_spliced[1][0:2]
        minute = capture_base_filename_spliced[1][2:4]
        second = capture_base_filename_spliced[1][4:6]

        post_filename = PATH_OF_WATCH_CAPTURES + "{}.md".format(capture_base_filename.replace('P.jpg', ''))

        filehandle = open(post_filename, "w+")
        filehandle.write("---\n")
        filehandle.write("layout: watch\n")
        filehandle.write("title: {} - {}/{}/{} - {}\n".format(station, day, month, year, capture_base_filename.replace('P.jpg', 'T.jpg')))
        filehandle.write("date: {}-{}-{} {}:{}:{}\n".format(year, month, day, hour, minute, second))
        filehandle.write("permalink: /{}/{}/{}/watch/{}\n".format(year, month, day, capture_base_filename.replace('P.jpg', '')))
        filehandle.write("capture: {}\n".format(file.replace('P.jpg', 'T.jpg')))
        filehandle.write("---\n")
        filehandle.close()

    return True


def generate_videos(connection: object) -> bool:
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    SELECT night_start, station
    FROM captures
    GROUP BY night_start, station
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        station = str(data[1])

        connection_cursor.execute("""
            SELECT id, night_start, station, files, files_full_path
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            file_input = capture[4].replace('P.jpg', '.avi')
            file_output = capture[4].replace('P.jpg', '.mp4')

            # if not os.path.exists(file_input) or os.path.exists(file_output):
            #     continue

            try:
                convert_video(file_input, file_output)
            except Exception:
                pass

    return True


def generate_analyzers(connection: object) -> bool:
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
            SELECT id, night_start, station, files, files_full_path
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            file = capture[4].replace('P.jpg', 'A.XML')

            if not os.path.exists(file):
                continue

            try:
                xmldoc = minidom.parse(file)
                itemlist = xmldoc.getElementsByTagName('ua2_object')
                classe = itemlist[0].attributes['class'].value
                magnitude = itemlist[0].attributes['mag'].value
                duration = itemlist[0].attributes['sec'].value
            except IndexError:
                classe = "__none__"
                magnitude = "__unknown__"
                duration = "__unknown__"
            except Exception:
                classe = "__none__"
                magnitude = "__none__"
                duration = "__none__"

            base = re.findall("\w{3}\d{1,2}.+", capture[3])

            filehandle = open(capture_filename, "a")
            filehandle.write("{}:\n".format(base[0]))
            filehandle.write("  station: {}\n".format(station))
            filehandle.write("  class: {}\n".format(classe))
            filehandle.write("  magnitude: {}\n".format(magnitude))
            filehandle.write("  duration: {}\n".format(duration))
            filehandle.close()

    return True


def get_date_list(days: int, date_format: str = '%Y%m%d'):
    return [(datetime.date.today() - datetime.timedelta(days=x)).strftime(date_format) for x in range(0, days)]


def get_matching_captures(captures_dir: list, prefix: str, days: int):
    result = []
    date_list = get_date_list(days)

    for directory in captures_dir:
        for date in date_list:
            files = glob.glob("{}/**/{}/*{}*P.jpg".format(directory, date, prefix), recursive=True)

            result.extend(files)

    return fix_path_delimiter(result)


def fix_path_delimiter(captures_list: list):
    result = []

    for path in captures_list:
        path_fixed = path.replace("\\", "/")

        result.append(path_fixed)

    return result


def cleanup_posts(days: int):
    result = []
    date_list = get_date_list(days, '%Y-%m-%d')

    for date in date_list:
        files = glob.glob("{}/{}-captures.md".format(PATH_OF_SITE_POSTS, date))

        result.extend(files)

    files_to_delete = fix_path_delimiter(result)

    for file_to_delete in files_to_delete:
        os.remove(file_to_delete)


def cleanup_captures(days: int, station_prefix: str = 'TLP'):
    result = []
    date_list = get_date_list(days, '%Y%m%d')

    for date in date_list:
        files = glob.glob("{}/{}*_{}.md".format(PATH_OF_SITE_CAPTURES, station_prefix, date))

        result.extend(files)

    files_to_delete = fix_path_delimiter(result)

    for file_to_delete in files_to_delete:
        os.remove(file_to_delete)


def cleanup_watches(days: int, station_prefix: str = 'TLP'):
    result = []
    date_list = get_date_list(days, '%Y%m%d')

    for date in date_list:
        files = glob.glob("{}/M{}_*_{}_*.md".format(PATH_OF_WATCH_CAPTURES, date, station_prefix))

        result.extend(files)

    files_to_delete = fix_path_delimiter(result)

    for file_to_delete in files_to_delete:
        os.remove(file_to_delete)


def convert_video(video_input: str, video_output: str):
    cmds = ['ffmpeg', '-n -i', video_input, '-c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p', video_output]
    subprocess.Popen(cmds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process captures files and create posts.')
    parser.add_argument('captures_dir', metavar='captures', type=str, nargs='+', help='captures directory input')
    parser.add_argument('days_back', metavar='days', type=int, default=5, help='number of days in the past')
    parser.add_argument('station_prefix', metavar='station', type=str, default='TLP', help='station prefix')

    args = parser.parse_args()

    print("- Connecting to database")
    connection = sqlite3.connect(':memory:')

    print("- Cleaning files")
    cleanup_posts(args.days_back)
    cleanup_captures(args.days_back, args.station_prefix)
    cleanup_watches(args.days_back, args.station_prefix)

    print('- Reading captures')
    captures = get_matching_captures(args.captures_dir, args.station_prefix, args.days_back)

    print("- Organizing captures")
    organize_captures(captures)

    print("- Converting videos")
    generate_videos(connection)

    print("- Creating captures")
    generate_captures(connection)

    print("- Creating pages")
    generate_posts(connection)

    print("- Creating watches")
    generate_watches(connection)

    print("- Creating analyzers")
    generate_analyzers(connection)

    print("- Closing database connection")
    connection.close()

    print("- Done :)")
